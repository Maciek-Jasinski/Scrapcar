"""
scrapcar/state.py
------------------
Kazdy monitor (config) x strona ma wlasny plik stanu w state/<slug>__<site>.json
z ofertami widzianymi przy ostatnim uruchomieniu. Dzieki temu dodanie nowego
configu nie rusza stanu innych monitorow.
"""

from __future__ import annotations

import json
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent.parent / "state"


def state_file_for(slug: str, site: str) -> Path:
    STATE_DIR.mkdir(exist_ok=True)
    return STATE_DIR / f"{slug}__{site}.json"


def load_seen(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_seen(path: Path, offers: dict) -> None:
    path.write_text(
        json.dumps(offers, ensure_ascii=False, indent=2), encoding="utf-8"
    )
