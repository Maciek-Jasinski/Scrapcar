#!/usr/bin/env python3
"""
automarket_scraper.py
----------------------
Sprawdza listing samochodów używanych na automarket.pl wg zadanych filtrów
i wysyła powiadomienie push (przez ntfy.sh) gdy pojawi się nowa oferta.

Filtry (marki na białej liście + reszta parametrów z podanego URL-a):
skoda, toyota, alfa-romeo, audi, bmw, kia, land-rover, lexus,
mazda, mercedes-benz, volkswagen, volvo
- ochrona gwarancyjna
- paliwo: Hybryda, PB
- skrzynia: automatyczna
- nadwozie: Kombi, Hatchback, Sedan, SUV
- przebieg <= 55 537 km
- pojemność silnika >= 1490 cm3
- moc >= 150 KM
- rata <= 3285 zł
- cena (zakup za gotówkę) <= 120 000 zł

Wymagania:
    pip install -r requirements.txt

Zmienne środowiskowe:
    NTFY_TOPIC  - nazwa tematu na ntfy.sh, na który wysyłane są powiadomienia
                  (jeśli pusta/nieustawiona, skrypt tylko wypisze wynik w konsoli)

Użycie lokalne:
    NTFY_TOPIC=twoj-tajny-temat python automarket_scraper.py
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

# --- KONFIGURACJA ---

# Marki wpisane bezpośrednio w ścieżkę URL (tak jak w linku od użytkownika) -
# zostawiamy jako literalny string, bo przecinki tu są częścią ścieżki, nie query.
BASE_PATH = (
    "https://automarket.pl/samochody/uzywane/wszystkie/"
    "skoda,toyota,alfa-romeo,audi,bmw,kia,land-rover,lexus,"
    "mazda,mercedes-benz,volkswagen,volvo"
)

FILTERS = {
    "warranty_protection": "1",
    "fuel_type": "Hybryda,PB",
    "gearbox_type": "Automatyczna",
    "body_style": "Hatchback,Sedan",
    "course": "*-55537",
    "engine_capacity": "1490-*",
    "power": "150-*",
    "installment": "*-3285",
    "installment_cash": "*-120000",
    "sort_by": "popular",
}

STATE_FILE = Path(__file__).resolve().parent / "automarket_seen_offers.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9",
}

# linki do ofert wyglądają np. tak: /oferta/bmw/x3/298655/leasing?f=...
# WAŻNE: bierzemy CAŁĄ ścieżkę (łącznie z segmentem typu finansowania na końcu),
# bo bez niego strona oferty zwraca 404.
OFFER_RE = re.compile(r"(/oferta/[a-z0-9\-']+/[a-z0-9\-']+/\d+/[a-z\-]+)")

MAX_PAGES = 300
REQUEST_DELAY_SEC = 1.0


def fetch_page(page: int) -> str:
    params = dict(FILTERS)
    params["page"] = page
    url = f"{BASE_PATH}?{urlencode(params, safe='*,')}"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_offers(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    offers = {}
    for a in soup.select('a[href*="/oferta/"]'):
        href = a.get("href", "")
        m = OFFER_RE.search(href)
        if not m:
            continue
        path = m.group(1)
        _, _, brand, model, offer_id, _offer_type = path.split("/")
        offers[offer_id] = {
            "id": offer_id,
            "brand": brand,
            "model": model,
            "url": f"https://automarket.pl{path}",
        }
    return offers


def collect_all_offers() -> dict:
    all_offers = {}
    page = 0
    while page < MAX_PAGES:
        html = fetch_page(page)
        page_offers = parse_offers(html)
        if not page_offers:
            break
        all_offers.update(page_offers)
        page += 1
        time.sleep(REQUEST_DELAY_SEC)
    return all_offers


def load_seen() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_seen(seen: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def notify_ntfy(offer: dict, topic: str) -> None:
    title = f"Automarket: {offer['brand'].upper()} {offer['model']}"
    url = f"https://ntfy.sh/{topic}"
    try:
        resp = requests.post(
            url,
            data=offer["url"].encode("utf-8"),
            headers={
                "Title": title,
                "Click": offer["url"],
                "Priority": "default",
                "Tags": "car",
            },
            timeout=10,
        )
        print(f"  [ntfy] POST {url} -> status {resp.status_code}: {resp.text.strip()[:200]}")
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [ntfy] BLAD wysylki powiadomienia: {exc}", file=sys.stderr)


def notify_telegram(offer: dict, bot_token: str, chat_id: str) -> None:
    text = f"{offer['brand'].upper()} {offer['model']}\n{offer['url']}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(
            url,
            data={"chat_id": chat_id, "text": text, "disable_web_page_preview": False},
            timeout=10,
        )
        print(f"  [telegram] POST -> status {resp.status_code}: {resp.text.strip()[:200]}")
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [telegram] BLAD wysylki powiadomienia: {exc}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report-first-run",
        action="store_true",
        help="Zglos wszystkie znalezione oferty jako 'nowe' nawet przy pierwszym uruchomieniu.",
    )
    args = parser.parse_args()

    ntfy_topic = os.environ.get("NTFY_TOPIC", "").strip()
    tg_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    is_first_run = not STATE_FILE.exists()

    try:
        all_offers = collect_all_offers()
    except requests.RequestException as exc:
        print(f"Blad podczas pobierania strony: {exc}", file=sys.stderr)
        sys.exit(1)

    seen = load_seen()

    if is_first_run and not args.report_first_run:
        new_ids = []
    else:
        new_ids = [oid for oid in all_offers if oid not in seen]

    if new_ids:
        print(f"Znaleziono {len(new_ids)} nowych ofert:\n")
        for oid in new_ids:
            o = all_offers[oid]
            print(f"- {o['brand'].upper()} {o['model']} -> {o['url']}")
            if ntfy_topic:
                notify_ntfy(o, ntfy_topic)
            if tg_bot_token and tg_chat_id:
                notify_telegram(o, tg_bot_token, tg_chat_id)
    elif is_first_run:
        print(
            f"Pierwsze uruchomienie: zapisano {len(all_offers)} ofert jako punkt startowy "
            "(nie sa zglaszane jako nowe)."
        )
    else:
        print("Brak nowych ofert.")

    seen.update(all_offers)
    save_seen(seen)


if __name__ == "__main__":
    main()
