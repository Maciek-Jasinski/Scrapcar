#!/usr/bin/env python3
"""
generate_readme.py
-------------------
Odswieza sekcje README.md z linkami do wyszukiwarek/stanu dla kazdego
monitora z configs/. Uruchamiane automatycznie w workflow po kazdym
sprawdzeniu ofert, ale mozna tez recznie:

    python generate_readme.py
"""

from scrapcar.config import load_all_configs
from scrapcar.readme_gen import update_readme


def main():
    configs = load_all_configs()
    update_readme(configs)
    print(f"README.md zaktualizowane ({len(configs)} monitorow).")


if __name__ == "__main__":
    main()
