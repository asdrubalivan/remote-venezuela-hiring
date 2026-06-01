"""CLI: render ``data/companies/*.yaml`` into a static site under ``site/``."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from .load_data import DATA_DIR, load_all_companies
from .models import Company, CompanyStatus, today_utc

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
TEMPLATES_DIR: Path = REPO_ROOT / "templates"
STATIC_DIR: Path = REPO_ROOT / "static"
DEFAULT_OUTPUT_DIR: Path = REPO_ROOT / "site"
JS_BUILD_SCRIPT: Path = REPO_ROOT / "scripts" / "build-js.mjs"


def _compile_frontend() -> None:
    """Compile src/ts/*.ts → static/*.js via the esbuild bundler.

    Runs only when Node is available *and* the TS sources exist. The compiled
    artifacts (static/filter.js, static/theme.js) are not committed; tests and
    CI regenerate them on demand. Setting ``RVH_SKIP_JS_BUILD=1`` skips it
    (useful for unit tests that don't care about the bundle's contents).
    """
    if os.environ.get("RVH_SKIP_JS_BUILD"):
        return
    if not JS_BUILD_SCRIPT.exists():
        return
    node = shutil.which("node")
    if not node:
        msg = (
            "Node.js is required to build the frontend bundle. "
            "Install Node or set RVH_SKIP_JS_BUILD=1."
        )
        raise RuntimeError(msg)
    try:
        subprocess.run(  # noqa: S603 - node path resolved via shutil.which; script path is repo-internal
            [node, str(JS_BUILD_SCRIPT)],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        msg = f"Frontend bundle build failed:\n{exc.stderr or exc.stdout}"
        raise RuntimeError(msg) from exc


STATUS_LABELS: dict[str, str] = {
    "accepts": "Probablemente acepta Venezuela",
    "rejects": "Reportada como no aceptante",
    "unknown": "Desconocido / necesita revisión",
}

STATUS_TAB_LABELS: dict[str, str] = {
    "all": "Todas",
    "accepts": "Acepta",
    "rejects": "No acepta",
    "unknown": "Desconocido",
}

VERIFICATION_LABELS: dict[str, str] = {
    "application_form": "Formulario de solicitud",
    "recruiter": "Reclutador/a",
    "public_job_post": "Oferta pública",
    "community_report": "Reporte comunitario",
    "unknown": "Desconocido",
}

PLATFORM_LABELS: dict[str, str] = {
    "greenhouse": "Greenhouse",
    "ashby": "Ashby",
    "lever": "Lever",
    "workable": "Workable",
    "teamtailor": "TeamTailor",
    "linkedin": "LinkedIn",
    "company_site": "Sitio de la empresa",
    "other": "Otra",
    "unknown": "Desconocido",
}

SPANISH_MONTHS: dict[int, str] = {
    1: "ene",
    2: "feb",
    3: "mar",
    4: "abr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dic",
}


def _format_date(d: date) -> str:
    """Return ``"15 may 2026"``-style date strings for the templates."""
    return f"{d.day} {SPANISH_MONTHS[d.month]} {d.year}"


def _make_env(templates_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.globals["status_labels"] = STATUS_LABELS
    env.globals["verification_labels"] = VERIFICATION_LABELS
    env.globals["platform_labels"] = PLATFORM_LABELS
    env.globals["format_date"] = _format_date
    return env


def _status_summary(companies: list[Company]) -> dict[str, int]:
    """Counts by status — also used as legacy ``summary`` for tests."""
    summary: dict[CompanyStatus, int] = dict.fromkeys(CompanyStatus, 0)
    for company in companies:
        summary[company.status] += 1
    return {status.value: count for status, count in summary.items()}


def _percent(part: int, total: int) -> int:
    return round(part / total * 100) if total else 0


def _stats_context(companies: list[Company]) -> dict[str, object]:
    """Pre-compute every aggregate the stats page renders."""
    active = [c for c in companies if not c.archived]
    archived = [c for c in companies if c.archived]
    stale_entries = sorted(
        (c for c in active if c.is_stale()),
        key=lambda c: c.last_checked,
    )

    status_counts = {
        "accepts": sum(1 for c in active if c.status == CompanyStatus.accepts),
        "rejects": sum(1 for c in active if c.status == CompanyStatus.rejects),
        "unknown": sum(1 for c in active if c.status == CompanyStatus.unknown),
    }
    status_pct = {k: _percent(v, len(active)) for k, v in status_counts.items()}

    def _bar_rows(counter: Counter[str]) -> list[tuple[str, int, int]]:
        total = sum(counter.values())
        return sorted(
            ((key, count, _percent(count, total)) for key, count in counter.items()),
            key=lambda row: row[1],
            reverse=True,
        )

    method_counter: Counter[str] = Counter(c.verification_method.value for c in active)
    platform_counter: Counter[str] = Counter(
        (c.hiring_platform.value if c.hiring_platform else "unknown") for c in active
    )

    return {
        "active_total": len(active),
        "archived_total": len(archived),
        "status_counts": status_counts,
        "status_pct": status_pct,
        "stale_count": len(stale_entries),
        "stale_entries": stale_entries,
        "method_counts": _bar_rows(method_counter),
        "platform_counts": _bar_rows(platform_counter),
        "today": today_utc(),
    }


def _index_context(companies: list[Company]) -> dict[str, object]:
    """Filter dropdown options + tab counts for the index page."""
    active = [c for c in companies if not c.archived]
    status_counts = _status_summary(active)

    methods = sorted({c.verification_method.value for c in companies})
    platforms = sorted(
        {(c.hiring_platform.value if c.hiring_platform else "unknown") for c in companies}
    )
    tags = sorted({tag for c in companies for tag in c.tags})

    def _tab(value: str, count: int) -> dict[str, object]:
        return {"value": value, "label": STATUS_TAB_LABELS[value], "count": count}

    status_tabs = [
        _tab("all", len(active)),
        _tab("accepts", status_counts.get("accepts", 0)),
        _tab("rejects", status_counts.get("rejects", 0)),
        _tab("unknown", status_counts.get("unknown", 0)),
    ]

    return {
        "verification_options": methods,
        "platform_options": platforms,
        "tag_options": tags,
        "status_tabs": status_tabs,
        "visible_count": len(active),
        "hero_accepts": status_counts.get("accepts", 0),
        "today": today_utc(),
    }


def _write_agents_txt(output_dir: Path) -> None:
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "# Proyecto de datos abiertos sobre empresas que contratan desde Venezuela.\n"
        "# Datos estructurados (YAML) disponibles en:\n"
        "# https://github.com/asdrubalivan/remote-venezuela-hiring/tree/main/data/companies\n"
    )
    (output_dir / "agents.txt").write_text(content, encoding="utf-8")


def build(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    data_dir: Path = DATA_DIR,
    templates_dir: Path = TEMPLATES_DIR,
    static_dir: Path = STATIC_DIR,
) -> Path:
    """Render the site and return the path to the generated ``index.html``."""
    companies = load_all_companies(data_dir)
    summary = _status_summary(companies)
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    _compile_frontend()
    env = _make_env(templates_dir)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    index_path = output_dir / "index.html"
    index_path.write_text(
        env.get_template("index.html").render(
            companies=companies,
            summary=summary,
            total=len(companies),
            generated_at=generated_at,
            home_url="./",
            stats_url="./stats.html",
            static_prefix="static",
            **_index_context(companies),
        ),
        encoding="utf-8",
    )

    stats_path = output_dir / "stats.html"
    stats_path.write_text(
        env.get_template("stats.html").render(
            companies=companies,
            generated_at=generated_at,
            home_url="./index.html",
            stats_url="./stats.html",
            static_prefix="static",
            **_stats_context(companies),
        ),
        encoding="utf-8",
    )

    company_dir = output_dir / "company"
    company_dir.mkdir()
    template_company = env.get_template("company.html")
    for company in companies:
        (company_dir / f"{company.id}.html").write_text(
            template_company.render(
                company=company,
                generated_at=generated_at,
                home_url="../index.html",
                stats_url="../stats.html",
                static_prefix="../static",
            ),
            encoding="utf-8",
        )

    if static_dir.exists():
        shutil.copytree(static_dir, output_dir / "static")

    _write_agents_txt(output_dir)

    return index_path


def main() -> int:
    try:
        index_path = build()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Site generated: {index_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
