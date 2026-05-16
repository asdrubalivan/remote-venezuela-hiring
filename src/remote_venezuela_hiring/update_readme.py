"""CLI: inject an auto-generated companies table into README.md."""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

from .build_site import (
    PLATFORM_LABELS,
    REPO_ROOT,
    SPANISH_MONTHS,
    STATUS_TAB_LABELS,
    VERIFICATION_LABELS,
)
from .load_data import DATA_DIR, load_all_companies

if TYPE_CHECKING:
    from datetime import date
    from pathlib import Path

    from .models import Company

MARKER_START = "<!-- COMPANIES_TABLE_START -->"
MARKER_END = "<!-- COMPANIES_TABLE_END -->"

STATUS_EMOJI: dict[str, str] = {
    "accepts": "✅",
    "rejects": "❌",
    "unknown": "❓",
}


def _sorted_active(companies: list[Company]) -> list[Company]:
    status_order = {"accepts": 0, "rejects": 1, "unknown": 2}
    active = [c for c in companies if not c.archived]
    return sorted(active, key=lambda c: (status_order[c.status.value], c.name.lower()))


def _fmt_date(d: date) -> str:
    return f"{d.day} {SPANISH_MONTHS[d.month]} {d.year}"


def generate_table(companies: list[Company]) -> str:
    rows = [
        "| Empresa | Estado | Plataforma | Método | Tags | Verificada |",
        "|:--------|:------:|:----------:|:------:|:----:|:----------:|",
    ]
    for c in _sorted_active(companies):
        name_cell = f"[{c.name}]({c.website_str()})"
        emoji = STATUS_EMOJI.get(c.status.value, "❓")
        label = STATUS_TAB_LABELS.get(c.status.value, c.status.value)
        status_cell = f"{emoji} {label}"
        platform_key = c.hiring_platform.value if c.hiring_platform else "unknown"
        platform = PLATFORM_LABELS.get(platform_key, "—")
        method = VERIFICATION_LABELS.get(c.verification_method.value, "—")
        tags = ", ".join(c.tags) if c.tags else "—"
        date_str = _fmt_date(c.last_checked)
        row = f"| {name_cell} | {status_cell} | {platform} | {method} | {tags} | {date_str} |"
        rows.append(row)
    return "\n".join(rows)


def inject_table(table_md: str, readme_path: Path) -> bool:
    """Return True if README was modified."""
    content = readme_path.read_text(encoding="utf-8")
    replacement = f"{MARKER_START}\n{table_md}\n{MARKER_END}"
    pattern = rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}"
    new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if n == 0:
        msg = (
            f"Markers not found in {readme_path}. "
            f"Add {MARKER_START} and {MARKER_END} to the README."
        )
        raise RuntimeError(msg)
    if new_content == content:
        return False
    readme_path.write_text(new_content, encoding="utf-8")
    return True


def main() -> None:
    readme = REPO_ROOT / "README.md"
    companies = load_all_companies(DATA_DIR)
    table = generate_table(companies)
    changed = inject_table(table, readme)
    active_count = len([c for c in companies if not c.archived])
    if changed:
        print(f"README.md updated with {active_count} companies.")
    else:
        print("README.md already up to date.")
    sys.exit(0)


if __name__ == "__main__":
    main()
