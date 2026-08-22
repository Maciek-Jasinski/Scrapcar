"""
scrapcar/sites/automarket.py
------------------------------
Adapter dla automarket.pl.

Oczekiwany ksztalt sekcji `automarket:` w YAML configu:

    automarket:
      brands: [volkswagen]        # lista marek, wchodzi do sciezki URL-a
      model: arteon                # opcjonalnie - tylko przy jednej marce w 'brands'
      filters:                    # reszta parametrow query string, 1:1 jak
        production_year: "2022-*" # w URL-u wyszukiwarki automarket.pl
        course: "*-70000"
        fuel_type: "PB"
        sort_by: popular

Wartosci filtrow to surowe stringi tak, jak automarket.pl przyjmuje je w URL-u
(np. zakresy "min-max" z gwiazdka jako brak ograniczenia). Najlatwiej je
podejrzec, ustawiajac filtry na stronie i kopiujac parametry z paska adresu.
"""

from __future__ import annotations

import re
from typing import Dict
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

NAME = "automarket"
DISPLAY_NAME = "Automarket"

BASE = "https://automarket.pl/samochody/uzywane/wszystkie"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9",
}

OFFER_RE = re.compile(r"(/oferta/[a-z0-9\-']+/[a-z0-9\-']+/\d+/[a-z\-]+)")

MAX_PAGES = 300
REQUEST_DELAY_SEC = 1.0


def build_search_url(site_cfg: dict, page: int = 0) -> str:
    brands = site_cfg.get("brands") or []
    if not brands:
        raise ValueError("Konfiguracja automarket wymaga niepustej listy 'brands'.")
    model = site_cfg.get("model")
    if model and len(brands) != 1:
        raise ValueError(
            "'model' w konfiguracji automarket dziala tylko przy jednej marce w 'brands' "
            "(automarket.pl wspiera filtr modelu tylko dla pojedynczej marki w sciezce URL-a)."
        )
    filters = dict(site_cfg.get("filters") or {})
    if page:
        filters["page"] = page
    brands_path = ",".join(brands)
    path = f"{BASE}/{brands_path}"
    if model:
        path += f"/{model}"
    query = urlencode(filters, safe="*,")
    return f"{path}?{query}"


def fetch_page(site_cfg: dict, page: int) -> str:
    url = build_search_url(site_cfg, page)
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_offers(html: str) -> Dict[str, dict]:
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


def collect_all_offers(site_cfg: dict) -> Dict[str, dict]:
    import time

    all_offers: Dict[str, dict] = {}
    page = 0
    while page < MAX_PAGES:
        html = fetch_page(site_cfg, page)
        page_offers = parse_offers(html)
        if not page_offers:
            break
        all_offers.update(page_offers)
        page += 1
        time.sleep(REQUEST_DELAY_SEC)
    return all_offers


def format_notification_title(offer: dict) -> str:
    return f"{offer['brand'].upper()} {offer['model']}"
