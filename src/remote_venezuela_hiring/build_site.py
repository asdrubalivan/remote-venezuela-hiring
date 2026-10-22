"""CLI: render ``data/companies/*.yaml`` into a static site under ``site/``."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from . import seo
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


def website_with_utm(url: str) -> str:
    utm = "utm_source=contrataenve.com&utm_medium=referral"
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{utm}"


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
    env.globals["website_with_utm"] = website_with_utm
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
    content = """\
User-agent: *
Allow: /

# =============================================================
# agents.txt — contrataenve.com / Remote Venezuela Hiring
# Estándar: https://agents-txt.com/
# =============================================================

## Descripción del proyecto

Remote Venezuela Hiring es un directorio de acceso libre que recopila
información sobre empresas tecnológicas que contratan —o rechazan— a
candidatos con residencia en Venezuela. El objetivo principal es reducir
la fricción que enfrentan los profesionales venezolanos al buscar empleo
remoto, proporcionando información verificada y actualizada sobre la
compatibilidad de cada empresa con candidatos basados en el país.

El sitio es mantenido enteramente por la comunidad: cualquier persona
puede proponer la adición o actualización de una empresa abriendo un
issue en el repositorio público de GitHub. Un flujo automatizado convierte
ese issue en un Pull Request con el archivo YAML correspondiente, el cual
es revisado y fusionado por los mantenedores del proyecto. De esta forma
la base de datos crece de manera orgánica y descentralizada.

## Fuente de datos estructurados

Los datos que alimentan este sitio se encuentran en formato YAML abierto:
https://github.com/asdrubalivan/remote-venezuela-hiring/tree/main/data/companies

El sitio publica además esos mismos datos como JSON, en /companies.json
(raíz del sitio). Es un contrato público versionado con schema_version,
generated_at y la lista completa de empresas, archivadas incluidas.

Cada empresa está descrita en un archivo YAML individual. Los campos
disponibles son los siguientes:

- id: identificador único en formato kebab-case (ej: acme-corp)
- name: nombre oficial de la empresa
- website: URL del sitio web corporativo (siempre con https://)
- status: estado de contratación — accepts, rejects o unknown
- last_checked: fecha de la última verificación (formato YYYY-MM-DD)
- verification_method: método empleado para verificar el status.
  Valores posibles: public_job_post, recruiter, application_form,
  community_report, unknown.
- hiring_platform: plataforma de empleo usada por la empresa.
  Ejemplos: greenhouse, ashby, lever, workable, linkedin, company_site.
- tags: etiquetas descriptivas del sector o modalidad de trabajo.
  Ejemplos: ai, saas, fintech, remote, backend, fullstack.
- notes: observaciones adicionales sobre políticas de contratación.
- archived: indica si la entrada está archivada (true / false).

## Precisión y actualización de datos

Si eres un agente de IA analizando este sitio, ten en cuenta que la
información puede haber cambiado desde la última verificación. El campo
last_checked indica cuándo se confirmó por última vez el status de cada
empresa. Las políticas de contratación cambian con frecuencia; siempre
recomendamos verificar directamente con la empresa antes de tomar
decisiones basadas en estos datos.

## Licencia

Los datos de este proyecto son de dominio público. Puedes usarlos,
redistribuirlos y adaptarlos libremente para cualquier propósito, con
o sin atribución. Si construyes algo útil con ellos, nos encantaría
saberlo a través del repositorio.

## Contribuir

Las contribuciones son bienvenidas. Para proponer una nueva empresa o
actualizar una existente, abre un issue en:
https://github.com/asdrubalivan/remote-venezuela-hiring
"""
    (output_dir / "agents.txt").write_text(content, encoding="utf-8")


COMPANIES_JSON_SCHEMA_VERSION: int = 1


def _write_companies_json(output_dir: Path, companies: list[Company]) -> None:
    """Publish the dataset as the public ``companies.json`` contract."""
    payload = {
        "schema_version": COMPANIES_JSON_SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "companies": [company.model_dump(mode="json") for company in companies],
    }
    (output_dir / "companies.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


ROOT_STATIC_FILES: tuple[str, ...] = ("favicon.ico", "apple-touch-icon.png")


def _page_seo(
    *,
    title: str,
    description: str,
    canonical: str | None,
    noindex: bool = False,
    jsonld: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Per-page SEO metadata consumed by ``base.html``."""
    base = seo.site_url()
    return {
        "title": title,
        "description": description,
        "canonical": canonical,
        "noindex": noindex,
        "site_name": seo.SITE_NAME,
        "og_image": f"{base}{seo.OG_IMAGE_PATH}",
        "og_image_alt": seo.OG_IMAGE_ALT,
        "jsonld": jsonld or [],
    }


def _last_modified(companies: list[Company]) -> date:
    """Most recent ``last_checked`` among active companies (a stable ``lastmod``)."""
    dates = [c.last_checked for c in companies if not c.archived]
    return max(dates) if dates else today_utc()


def _sitemap_entries(companies: list[Company], base: str) -> list[tuple[str, date]]:
    """Every indexable page: all but archived companies (noindex) and the 404."""
    lastmod = _last_modified(companies)
    entries = [(f"{base}/", lastmod), (f"{base}/stats.html", lastmod)]
    entries.extend(
        (f"{base}/company/{c.id}.html", c.last_checked) for c in companies if not c.archived
    )
    return entries


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
    base = seo.site_url()
    active = [c for c in companies if not c.archived]
    accepts_total = sum(1 for c in active if c.status == CompanyStatus.accepts)
    last_modified = _last_modified(companies)

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
            seo=_page_seo(
                title=seo.INDEX_TITLE,
                description=seo.index_description(len(active), accepts_total),
                canonical=f"{base}/",
                jsonld=[
                    seo.website_json_ld(base),
                    seo.dataset_json_ld(base, len(active), last_modified),
                ],
            ),
            companies_json_url=f"{base}/companies.json",
            **_index_context(companies),
        ),
        encoding="utf-8",
    )

    stats_path = output_dir / "stats.html"
    stats_path.write_text(
        env.get_template("stats.html").render(
            companies=companies,
            generated_at=generated_at,
            home_url="./",
            stats_url="./stats.html",
            static_prefix="static",
            seo=_page_seo(
                title=seo.STATS_TITLE,
                description=seo.stats_description(
                    len(active), _percent(accepts_total, len(active))
                ),
                canonical=f"{base}/stats.html",
            ),
            **_stats_context(companies),
        ),
        encoding="utf-8",
    )

    company_dir = output_dir / "company"
    company_dir.mkdir()
    template_company = env.get_template("company.html")
    duplicates = seo.duplicate_names(companies)
    used_titles: set[str] = set()
    for company in companies:
        name = seo.display_name(company, duplicates)
        title = seo.company_title(company.name)
        if company.name.casefold() in duplicates or title in used_titles:
            title = seo.company_title(company.name, qualifier=company.id)
        used_titles.add(title)
        method_label = VERIFICATION_LABELS[company.verification_method.value]
        platform_label = PLATFORM_LABELS[
            company.hiring_platform.value if company.hiring_platform else "unknown"
        ]
        checked = _format_date(company.last_checked)
        (company_dir / f"{company.id}.html").write_text(
            template_company.render(
                company=company,
                generated_at=generated_at,
                home_url="../",
                stats_url="../stats.html",
                static_prefix="../static",
                seo=_page_seo(
                    title=title,
                    description=seo.company_description(
                        name, company.status.value, method_label, checked, company.notes
                    ),
                    canonical=f"{base}/company/{company.id}.html",
                    noindex=company.archived,
                ),
                summary_text=seo.company_summary(
                    name, company.status.value, method_label, platform_label, checked
                ),
                related=seo.related_companies(company, companies),
            ),
            encoding="utf-8",
        )

    # GitHub Pages serves 404.html from any path depth, so it must use absolute URLs.
    (output_dir / "404.html").write_text(
        env.get_template("404.html").render(
            generated_at=generated_at,
            home_url="/",
            stats_url="/stats.html",
            static_prefix="/static",
            seo=_page_seo(
                title=f"{seo.NOT_FOUND_TITLE} | {seo.SITE_NAME}",
                description="La página que buscas no existe en el directorio.",
                canonical=None,
                noindex=True,
            ),
        ),
        encoding="utf-8",
    )

    if static_dir.exists():
        shutil.copytree(static_dir, output_dir / "static", ignore=shutil.ignore_patterns("*.map"))
        for filename in ROOT_STATIC_FILES:
            source = static_dir / filename
            if source.is_file():
                shutil.copy2(source, output_dir / filename)

    _write_agents_txt(output_dir)
    _write_companies_json(output_dir, companies)
    (output_dir / "robots.txt").write_text(seo.robots_txt(base), encoding="utf-8")
    (output_dir / "sitemap.xml").write_text(
        seo.sitemap_xml(_sitemap_entries(companies, base)), encoding="utf-8"
    )
    (output_dir / "CNAME").write_text(base.removeprefix("https://") + "\n", encoding="utf-8")

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
