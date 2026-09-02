"""
scrapcar/notify.py
-------------------
Wysylka powiadomien push. Kazde powiadomienie jest podpisane nazwa
monitora (configu), zeby od razu bylo wiadomo, ktory filtr go zlapal.
"""

from __future__ import annotations

import sys
import unicodedata

import requests


def _ascii_header(value: str) -> str:
    """ntfy/urllib3 wymagaja naglowkow kodowalnych w latin-1/ASCII.
    Zamieniamy polskie znaki diakrytyczne na najblizszy odpowiednik ASCII,
    zeby uniknac UnicodeEncodeError przy wysylce (np. tytuly ofert z 'ł', 'ą', itd).
    """
    # normalize("NFKD") nie rozbija polskiego 'ł'/'Ł' (brak dekompozycji Unicode),
    # wiec podmieniamy je recznie PRZED encode(..., "ignore"), inaczej zostalyby
    # bezpowrotnie usuniete zamiast zamienione na 'l'/'L'.
    value = value.replace("\u0142", "l").replace("\u0141", "L")
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_only


def notify_ntfy(monitor_name: str, site_display_name: str, title: str, url: str, topic: str) -> None:
    full_title = f"[{monitor_name}] {site_display_name}: {title}"
    ntfy_url = f"https://ntfy.sh/{topic}"
    try:
        resp = requests.post(
            ntfy_url,
            data=url.encode("utf-8"),
            headers={
                "Title": _ascii_header(full_title),
                "Click": url,
                "Priority": "default",
                "Tags": "car",
            },
            timeout=10,
        )
        print(f"  [ntfy] POST {ntfy_url} -> status {resp.status_code}: {resp.text.strip()[:200]}")
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [ntfy] BLAD wysylki powiadomienia: {exc}", file=sys.stderr)


def notify_telegram(monitor_name: str, site_display_name: str, title: str, url: str, bot_token: str, chat_id: str) -> None:
    text = f"[{monitor_name}] {site_display_name}: {title}\n{url}"
    tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(
            tg_url,
            data={"chat_id": chat_id, "text": text, "disable_web_page_preview": False},
            timeout=10,
        )
        print(f"  [telegram] POST -> status {resp.status_code}: {resp.text.strip()[:200]}")
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [telegram] BLAD wysylki powiadomienia: {exc}", file=sys.stderr)
