"""
scrapcar/config.py
-------------------
Wczytuje pliki konfiguracyjne z katalogu configs/. Kazdy plik = jeden
niezalezny "monitor" (np. "VW Arteon benzyna"), ktory moze sledzic jedna
albo obie strony (automarket, findcar) z wlasnymi filtrami.

Zeby dodac nowy monitor: skopiuj configs/_przyklad.yaml, zmien nazwe pliku
i wartosci filtrow. Nic wiecej nie trzeba ruszac - runner.py i
generate_readme.py same je znajda.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"

# nazwy plikow, ktore nie sa konfiguracjami monitorow (dokumentacja/przyklad)
IGNORED_PREFIXES = ("_",)

SUPPORTED_SITES = ("automarket", "findcar")


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


@dataclass
class MonitorConfig:
    slug: str
    name: str
    source_file: Path
    sites: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def active_sites(self):
        return [s for s in SUPPORTED_SITES if s in self.sites]


def load_config_file(path: Path) -> MonitorConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    name = data.get("name") or path.stem
    slug = _slugify(data.get("slug") or path.stem)

    sites: Dict[str, Dict[str, Any]] = {}
    for site in SUPPORTED_SITES:
        if site in data and data[site]:
            sites[site] = data[site]

    if not sites:
        raise ValueError(
            f"Konfiguracja '{path.name}' nie zawiera zadnej sekcji "
            f"({' / '.join(SUPPORTED_SITES)}) z filtrami."
        )

    return MonitorConfig(slug=slug, name=name, source_file=path, sites=sites)


def load_all_configs(configs_dir: Optional[Path] = None) -> list[MonitorConfig]:
    configs_dir = configs_dir or CONFIGS_DIR
    configs = []
    for path in sorted(configs_dir.glob("*.yaml")) + sorted(configs_dir.glob("*.yml")):
        if path.name.startswith(IGNORED_PREFIXES):
            continue
        configs.append(load_config_file(path))

    slugs_seen = {}
    for cfg in configs:
        if cfg.slug in slugs_seen:
            raise ValueError(
                f"Dwie konfiguracje maja ten sam slug '{cfg.slug}': "
                f"{slugs_seen[cfg.slug].name} i {cfg.source_file.name}. "
                "Nadaj jednej z nich pole 'slug' w YAML, zeby je odroznic."
            )
        slugs_seen[cfg.slug] = cfg.source_file

    return configs
