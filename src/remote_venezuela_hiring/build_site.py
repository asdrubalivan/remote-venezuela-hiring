"""CLI: render ``data/companies/*.yaml`` into a static site under ``site/``."""

from __future__ import annotations

import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from .load_data import DATA_DIR, load_all_companies
from .models import Company, CompanyStatus

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
TEMPLATES_DIR: Path = REPO_ROOT / "templates"
STATIC_DIR: Path = REPO_ROOT / "static"
DEFAULT_OUTPUT_DIR: Path = REPO_ROOT / "site"


def _make_env(templates_dir: Path) -> Environment:
    """Build a Jinja2 environment configured for safe HTML rendering."""
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def _company_summary(companies: list[Company]) -> dict[str, int]:
    """Return counts by status for the page header."""
    summary = dict.fromkeys(CompanyStatus, 0)
    for company in companies:
        summary[company.status] += 1
    return {status.value: count for status, count in summary.items()}


def build(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    data_dir: Path = DATA_DIR,
    templates_dir: Path = TEMPLATES_DIR,
    static_dir: Path = STATIC_DIR,
) -> Path:
    """Render the site and return the path to the generated ``index.html``.

    Args:
        output_dir: where the rendered site is written. Created if missing,
            wiped clean otherwise.
        data_dir: where company YAML files live.
        templates_dir: where Jinja2 templates live.
        static_dir: where CSS/JS assets live (copied verbatim to ``output_dir``).
    """
    companies = load_all_companies(data_dir)
    summary = _company_summary(companies)

    env = _make_env(templates_dir)
    template = env.get_template("index.html")
    html = template.render(
        companies=companies,
        summary=summary,
        total=len(companies),
        generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
    )

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    index_path = output_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    if static_dir.exists():
        shutil.copytree(static_dir, output_dir / "static")

    return index_path


def main() -> int:
    """Entry point for ``rvh-build-site``."""
    try:
        index_path = build()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Site generated: {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
