#!/usr/bin/env python3
"""
run.py
------
Odpala wszystkie monitory zdefiniowane w configs/ (albo wybrane, przez --only).

Przyklady:
    python run.py
    python run.py --report-first-run
    python run.py --only arteon-benzyna
    python run.py --only arteon-benzyna multi-marka-hybryda-pb

Zmienne srodowiskowe:
    NTFY_TOPIC          - nazwa tematu na ntfy.sh (opcjonalne)
    TELEGRAM_BOT_TOKEN   - token bota Telegram
    TELEGRAM_CHAT_ID     - chat_id odbiorcy
"""

import argparse
import os

from scrapcar.config import load_all_configs
from scrapcar.runner import RunOptions, run_all


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report-first-run",
        action="store_true",
        help="Zglos wszystkie znalezione oferty jako 'nowe' nawet przy pierwszym uruchomieniu configu.",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="SLUG",
        help="Uruchom tylko wskazane monitory (slug = nazwa pliku YAML bez rozszerzenia, "
             "chyba ze plik ma wlasne pole 'slug').",
    )
    args = parser.parse_args()

    configs = load_all_configs()
    if not configs:
        print("Brak konfiguracji w configs/. Skopiuj configs/_przyklad.yaml i uzupelnij filtry.")
        return

    opts = RunOptions(report_first_run=args.report_first_run, only_slugs=args.only)

    ntfy_topic = os.environ.get("NTFY_TOPIC", "").strip()
    tg_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    run_all(configs, opts, ntfy_topic, tg_bot_token, tg_chat_id)


if __name__ == "__main__":
    main()
