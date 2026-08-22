"""
scrapcar/readme_gen.py
------------------------
Generuje sekcje README.md miedzy znacznikami
<!-- MONITORS:START --> ... <!-- MONITORS:END -->
na podstawie configow z configs/. Kazdy monitor dostaje naglowek i linki
markdown ([Automarket](dlugi-url)) - dlugi URL jest "zaszyty" pod krotkim
tekstem, wiec czytelny widok README nie jest zasmiecony.
"""

from __future__ import annotations

from pathlib import Path

from .config import MonitorConfig
from .sites import SITE_MODULES

README_PATH = Path(__file__).resolve().parent.parent / "README.md"
STATE_REPO_BASE = "https://github.com/Maciek-Jasinski/Scrapcar/blob/main/state"

START_MARKER = "<!-- MONITORS:START -->"
END_MARKER = "<!-- MONITORS:END -->"


def render_monitor_section(cfg: MonitorConfig) -> str:
    lines = [f"### {cfg.name}", ""]
    for site_name in cfg.active_sites():
        module = SITE_MODULES[site_name]
        site_cfg = cfg.sites[site_name]
        url = module.build_search_url(site_cfg)
        lines.append(f"- [Szukaj na {module.DISPLAY_NAME}]({url})")
    lines.append("")
    lines.append("Zapisany stan (co skrypt aktualnie \"wie\"):")
    for site_name in cfg.active_sites():
        module = SITE_MODULES[site_name]
        state_url = f"{STATE_REPO_BASE}/{cfg.slug}__{site_name}.json"
        lines.append(f"- [{module.DISPLAY_NAME}]({state_url})")
    lines.append("")
    return "\n".join(lines)


def render_all_monitors(configs: list[MonitorConfig]) -> str:
    if not configs:
        return "_Brak skonfigurowanych monitorow w configs/._\n"
    sections = [render_monitor_section(cfg) for cfg in configs]
    return "\n".join(sections).rstrip() + "\n"


def update_readme(configs: list[MonitorConfig], readme_path: Path = README_PATH) -> None:
    content = readme_path.read_text(encoding="utf-8")
    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError(
            f"README.md nie zawiera znacznikow {START_MARKER} / {END_MARKER}."
        )
    before, rest = content.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    new_section = render_all_monitors(configs)
    new_content = f"{before}{START_MARKER}\n\n{new_section}\n{END_MARKER}{after}"
    readme_path.write_text(new_content, encoding="utf-8")
