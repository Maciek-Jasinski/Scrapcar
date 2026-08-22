"""
scrapcar/sites/findcar.py
----------------------------
Adapter dla findcar.pl.

Oczekiwany ksztalt sekcji `findcar:` w YAML configu:

    findcar:
      filters:                      # 1:1 parametry query string findcar.pl
        makes: volkswagen
        models: arteon
        fuelTypes: petrol
        yearMin: "2022"
        mileageMax: "70000"
        conditions: vehicle_used
        size: "45"

Najlatwiej podejrzec te wartosci, ustawiajac filtry na findcar.pl i
kopiujac parametry z paska adresu.
"""

from __future__ import annotations

import re
from typing import Dict
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

NAME = "findcar"
DISPLAY_NAME = "FindCar"

BASE = "https://findcar.pl/znajdz-samochod"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9",
}

OFFER_RE = re.compile(r"/oferty-dealerow/([a-z0-9\-]+)")

MAX_PAGES = 100
REQUEST_DELAY_SEC = 1.0


def build_search_url(site_cfg: dict, page: int = 1) -> str:
    filters = dict(site_cfg.get("filters") or {})
    query = urlencode(filters, safe=",")
    if page and page > 1:
        return f"{BASE}/{page}?{query}"
    return f"{BASE}?{query}"


def fetch_page(site_cfg: dict, page: int) -> str:
    url = build_search_url(site_cfg, page)
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_offers(html: str) -> Dict[str, dict]:
    soup = BeautifulSoup(html, "html.parser")
    offers = {}
    for a in soup.select('a[href*="/oferty-dealerow/"]'):
        href = a.get("href", "")
        m = OFFER_RE.search(href)
        if not m:
            continue
        slug = m.group(1).split("?")[0].rstrip("/")
        parts = slug.split("-")
        offer_id = parts[-1]
        if not offer_id.isdigit():
            continue
        brand = parts[0]
        title = a.get_text(strip=True) or slug
        offers[offer_id] = {
            "id": offer_id,
            "brand": brand,
            "title": title,
            "url": f"https://findcar.pl/oferty-dealerow/{slug}",
        }
    return offers


def collect_all_offers(site_cfg: dict) -> Dict[str, dict]:
    import time

    all_offers: Dict[str, dict] = {}
    page = 1
    while page <= MAX_PAGES:
        html = fetch_page(site_cfg, page)
        page_offers = parse_offers(html)
        if not page_offers:
            break
        all_offers.update(page_offers)
        page += 1
        time.sleep(REQUEST_DELAY_SEC)
    return all_offers


def format_notification_title(offer: dict) -> str:
    return offer["title"]
