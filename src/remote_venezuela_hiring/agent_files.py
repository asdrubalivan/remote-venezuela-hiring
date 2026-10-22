"""Files meant for AI agents: ``llms.txt``, ``agents.txt``/``agents.json`` and Markdown pages.

Everything here is pure (no I/O): the build writes the returned strings to disk.
Markdown versions are published next to the HTML ones (``index.md`` and
``company/<id>.md``) as proposed by https://llmstxt.org, and ``agents.txt`` follows
https://agents-txt.com (comment lines plus capability directives only).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from . import seo
from .models import STALE_AFTER_DAYS, CompanyStatus

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from datetime import date

    from .models import Company

AGENTS_STANDARD_URL: Final[str] = "https://agents-txt.com"
AGENTS_JSON_SCHEMA_URL: Final[str] = "https://agents-txt.com/schema/agents-json/v1.0.json"
AGENTS_JSON_VERSION: Final[str] = "1.0"

SITE_SUMMARY: Final[str] = (
    "Directorio comunitario y de acceso libre de empresas que contratan, o rechazan, "
    "a candidatos con residencia en Venezuela."
)
WEBMCP_DESCRIPTION: Final[str] = (
    "Herramientas WebMCP para listar y consultar empresas del directorio."
)
DISCLAIMER: Final[str] = (
    "No es asesoramiento legal ni una declaración oficial de ninguna empresa. "
    "La información la aporta la comunidad y puede estar desactualizada: "
    "verifica siempre directamente con la empresa."
)
LICENSE_LINE: Final[str] = "Código y datos bajo licencia MIT (https://opensource.org/licenses/MIT)."

STATUS_ORDER: Final[tuple[CompanyStatus, ...]] = (
    CompanyStatus.accepts,
    CompanyStatus.rejects,
    CompanyStatus.unknown,
)


@dataclass(frozen=True)
class Labels:
    """Human-readable labels for the enum values used in the dataset."""

    status: Mapping[str, str]
    method: Mapping[str, str]
    platform: Mapping[str, str]

    def platform_of(self, company: Company) -> str:
        return self.platform[
            company.hiring_platform.value if company.hiring_platform else "unknown"
        ]


def markdown_url(base: str, company_id: str | None = None) -> str:
    """Absolute URL of the Markdown version of the index or of a company page."""
    if company_id is None:
        return f"{base}/index.md"
    return f"{base}/company/{company_id}.md"


def freshness_sentence(age_days: int, *, stale: bool) -> str:
    """How recent the last verification is, in plain words for readers and agents."""
    if stale:
        return (
            f"Esta entrada está desactualizada: se verificó por última vez hace {age_days} "
            f"días (más de {STALE_AFTER_DAYS})."
        )
    if age_days <= 0:
        return "Verificada hoy."
    if age_days == 1:
        return "Verificada hace 1 día."
    return f"Verificada hace {age_days} días."


def _link_text(text: str) -> str:
    return text.replace("[", "(").replace("]", ")")


def _active(companies: Iterable[Company]) -> list[Company]:
    return [c for c in companies if not c.archived]


def _by_status(companies: Iterable[Company]) -> dict[CompanyStatus, list[Company]]:
    groups: dict[CompanyStatus, list[Company]] = {status: [] for status in STATUS_ORDER}
    for company in _active(companies):
        groups[company.status].append(company)
    for group in groups.values():
        group.sort(key=lambda c: (c.name.casefold(), c.id))
    return groups


def _site_blurb(groups: Mapping[CompanyStatus, Sequence[Company]]) -> str:
    """Blockquote summary shared by ``llms.txt`` and ``index.md``."""
    total = sum(len(group) for group in groups.values())
    accepts = len(groups[CompanyStatus.accepts])
    return (
        f"> {SITE_SUMMARY} Contiene {total} empresas activas; "
        f"{accepts} probablemente aceptan candidatos desde Venezuela."
    )


def _entry_line(base: str, company: Company, name: str, labels: Labels) -> str:
    notes = [labels.platform_of(company), f"verificada {company.last_checked.isoformat()}"]
    if company.is_stale():
        notes.append("desactualizada")
    return f"- [{_link_text(name)}]({markdown_url(base, company.id)}): {' · '.join(notes)}"


def company_markdown(
    company: Company,
    *,
    base: str,
    name: str,
    labels: Labels,
    summary: str,
    related: Sequence[Company],
) -> str:
    """Markdown version of a company page (``company/<id>.md``)."""
    verified = company.last_checked.isoformat()
    if company.is_stale():
        verified += " (desactualizada)"
    lines = [
        f"# {name}: ¿contrata desde Venezuela?",
        "",
        f"> {summary}",
        "",
        f"- Estado: {labels.status[company.status.value]} (`{company.status.value}`)",
        f"- Sitio web: {company.website_str()}",
        f"- Método de verificación: {labels.method[company.verification_method.value]}",
        f"- Plataforma de empleo: {labels.platform_of(company)}",
        f"- Última verificación: {verified}",
    ]
    if company.tags:
        lines.append(f"- Etiquetas: {', '.join(company.tags)}")
    if company.notes and seo.normalize_text(company.notes):
        lines += ["", "## Notas de la comunidad", "", seo.normalize_text(company.notes)]
    if related:
        lines += ["", "## Empresas similares", ""]
        lines += [
            f"- [{_link_text(other.name)}]({markdown_url(base, other.id)}): "
            f"{labels.status[other.status.value]}"
            for other in related
        ]
    lines += [
        "",
        "## Fuente",
        "",
        f"- Página HTML: {base}/company/{company.id}.html",
        f"- Registro en GitHub: {seo.GITHUB_URL}/blob/main/data/companies/{company.id}.yaml",
        f"- Dataset completo (JSON): {base}/companies.json",
        f"- Índice del directorio: {markdown_url(base)}",
        "",
        f"{DISCLAIMER} {LICENSE_LINE}",
    ]
    return "\n".join(lines) + "\n"


def index_markdown(
    companies: Sequence[Company], *, base: str, labels: Labels, last_modified: date
) -> str:
    """Markdown version of the home page (``index.md``): every active company by status."""
    groups = _by_status(companies)
    duplicates = seo.duplicate_names(companies)
    lines = [
        f"# {seo.INDEX_TITLE.capitalize()}",
        "",
        _site_blurb(groups),
        "",
        (
            f"Datos actualizados hasta el {last_modified.isoformat()}. "
            f"Versión HTML: [{seo.SITE_ALTERNATE_NAME}]({base}/) · "
            f"Dataset completo: [companies.json]({base}/companies.json) · "
            f"Guía para agentes: [llms.txt]({base}/llms.txt)"
        ),
        "",
        f"{DISCLAIMER} {LICENSE_LINE}",
    ]
    for status in STATUS_ORDER:
        group = groups[status]
        lines += ["", f"## {labels.status[status.value]} ({len(group)})", ""]
        lines += [
            _entry_line(base, company, seo.display_name(company, duplicates), labels)
            for company in group
        ]
    return "\n".join(lines) + "\n"


def llms_txt(
    companies: Sequence[Company], *, base: str, labels: Labels, last_modified: date
) -> str:
    """The ``llms.txt`` index (format from https://llmstxt.org)."""
    groups = _by_status(companies)
    duplicates = seo.duplicate_names(companies)
    lines = [
        f"# {seo.SITE_NAME}",
        "",
        _site_blurb(groups),
        "",
        (
            "Cada empresa tiene un estado (`accepts`, `rejects` o `unknown`), un método de "
            "verificación y la fecha de la última verificación; las entradas con más de "
            f"{STALE_AFTER_DAYS} días sin verificar se marcan como desactualizadas. "
            f"Datos actualizados hasta el {last_modified.isoformat()}. {DISCLAIMER} {LICENSE_LINE}"
        ),
        "",
        "## Datos",
        "",
        f"- [Índice en Markdown]({markdown_url(base)}): todas las empresas agrupadas por estado",
        f"- [Dataset completo]({base}/companies.json): JSON versionado, incluye las archivadas",
        f"- [Estadísticas]({base}/stats.html): totales por estado, método y plataforma",
    ]
    for status in STATUS_ORDER:
        group = groups[status]
        lines += ["", f"## {labels.status[status.value]} ({len(group)})", ""]
        lines += [
            _entry_line(base, company, seo.display_name(company, duplicates), labels)
            for company in group
        ]
    lines += [
        "",
        "## Optional",
        "",
        f"- [Repositorio en GitHub]({seo.GITHUB_URL}): código, datos YAML y cómo contribuir",
        f"- [agents.txt]({base}/agents.txt): capacidades para agentes (WebMCP)",
        f"- [Sitemap]({base}/sitemap.xml): páginas HTML indexables",
    ]
    return "\n".join(lines) + "\n"


def agents_txt(base: str) -> str:
    """The ``agents.txt`` file: only comments and capability directives (agents-txt.com)."""
    lines = [
        "# agents.txt",
        f"# Standard: {AGENTS_STANDARD_URL}",
        f"# JSON: {base}/agents.json",
        "#",
        f"# {seo.SITE_NAME} ({seo.SITE_ALTERNATE_NAME})",
        f"# {SITE_SUMMARY}",
        "#",
        f"# Guía para modelos de lenguaje: {base}/llms.txt",
        f"# Dataset completo (JSON): {base}/companies.json",
        f"# Páginas en Markdown: {markdown_url(base)} y {base}/company/<id>.md",
        f"# Código y datos YAML: {seo.GITHUB_URL}",
        f"# {LICENSE_LINE}",
        "#",
        "# Las páginas HTML registran herramientas WebMCP (list_companies, get_company).",
        "",
        f"WebMCP: {base}/",
    ]
    return "\n".join(lines) + "\n"


def agents_json(base: str) -> str:
    """The ``agents.json`` companion, valid against the agents-txt.com v1.0 schema."""
    payload = {
        "$schema": AGENTS_JSON_SCHEMA_URL,
        "version": AGENTS_JSON_VERSION,
        "standard": AGENTS_STANDARD_URL,
        "site": {"name": seo.SITE_NAME, "url": f"{base}/", "description": SITE_SUMMARY},
        "webmcp": [{"url": f"{base}/", "description": WEBMCP_DESCRIPTION}],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
