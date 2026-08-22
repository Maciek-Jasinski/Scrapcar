"""
scrapcar/sites/base.py
-----------------------
Wspolny interfejs, jaki musi implementowac kazdy modul w sites/.
Kazda strona (automarket, findcar...) ma swoj wlasny uklad URL-i i HTML-a,
wiec adapter dostaje surowa konfiguracje (dict z YAML-a) i sam wie, jak z niej
zbudowac URL oraz jak sparsowac wyniki.
"""

from __future__ import annotations

from typing import Dict, Protocol


class SiteAdapter(Protocol):
    NAME: str
    HEADERS: Dict[str, str]

    def build_search_url(self, site_cfg: dict, page: int) -> str:
        """Buduje pelny URL wyszukiwania (do requestow i do README)."""
        ...

    def fetch_page(self, site_cfg: dict, page: int) -> str:
        """Pobiera HTML danej strony wynikow."""
        ...

    def parse_offers(self, html: str) -> Dict[str, dict]:
        """Zwraca {offer_id: {id, url, ...}} znalezione w HTML-u."""
        ...

    def format_notification_title(self, offer: dict) -> str:
        """Tytul powiadomienia (bez nazwy monitora, ta jest dodawana wyzej)."""
        ...
