"""
scrapcar/runner.py
-------------------
Odpala kazdy monitor (config) na kazdej skonfigurowanej dla niego stronie,
porownuje wyniki ze stanem z poprzedniego uruchomienia i wysyla powiadomienia
o nowych ofertach.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

import requests

from .config import MonitorConfig
from .notify import notify_ntfy, notify_telegram
from .sites import SITE_MODULES
from .state import load_seen, save_seen, state_file_for


@dataclass
class RunOptions:
    report_first_run: bool = False
    only_slugs: list[str] | None = None


def run_config_on_site(cfg: MonitorConfig, site_name: str, opts: RunOptions,
                        ntfy_topic: str, tg_bot_token: str, tg_chat_id: str) -> None:
    module = SITE_MODULES[site_name]
    site_cfg = cfg.sites[site_name]
    state_path = state_file_for(cfg.slug, site_name)
    is_first_run = not state_path.exists()

    print(f"\n== [{cfg.name}] {module.DISPLAY_NAME} ==")

    try:
        all_offers = module.collect_all_offers(site_cfg)
    except requests.RequestException as exc:
        print(f"  BLAD podczas pobierania strony: {exc}", file=sys.stderr)
        return

    seen = load_seen(state_path)

    if is_first_run and not opts.report_first_run:
        new_ids = []
    else:
        new_ids = [oid for oid in all_offers if oid not in seen]

    removed_ids = [oid for oid in seen if oid not in all_offers]

    if new_ids:
        print(f"  Znaleziono {len(new_ids)} nowych ofert:")
        for oid in new_ids:
            o = all_offers[oid]
            title = module.format_notification_title(o)
            print(f"  - {title} -> {o['url']}")
            if ntfy_topic:
                notify_ntfy(cfg.name, module.DISPLAY_NAME, title, o["url"], ntfy_topic)
            if tg_bot_token and tg_chat_id:
                notify_telegram(cfg.name, module.DISPLAY_NAME, title, o["url"], tg_bot_token, tg_chat_id)
    elif is_first_run:
        print(
            f"  Pierwsze uruchomienie: zapisano {len(all_offers)} ofert jako punkt "
            "startowy (nie sa zglaszane jako nowe)."
        )
    else:
        print("  Brak nowych ofert.")

    if removed_ids:
        print(f"  Usunieto {len(removed_ids)} ofert, ktorych juz nie ma w wynikach.")

    save_seen(state_path, all_offers)


def run_all(configs: list[MonitorConfig], opts: RunOptions,
            ntfy_topic: str, tg_bot_token: str, tg_chat_id: str) -> None:
    for cfg in configs:
        if opts.only_slugs and cfg.slug not in opts.only_slugs:
            continue
        for site_name in cfg.active_sites():
            run_config_on_site(cfg, site_name, opts, ntfy_topic, tg_bot_token, tg_chat_id)
