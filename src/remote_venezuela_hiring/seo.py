"""SEO helpers: titles, descriptions, sitemap, robots.txt, JSON-LD and related links.

Everything here is pure (no I/O) except :func:`site_url`, which reads the
``RVH_SITE_URL`` override. Titles and descriptions are truncated at word
boundaries so a valid data PR can never fail the build over a long name.
"""

from __future__ import annotations

import os
import re
from collections import Counter
from typing import TYPE_CHECKING, Final
from xml.sax.saxutils import escape

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from .models import Company

DEFAULT_SITE_URL: Final[str] = "https://contrataenve.com"
SITE_NAME: Final[str] = "Remote Venezuela Hiring"
SITE_ALTERNATE_NAME: Final[str] = "contrataenve.com"
GITHUB_URL: Final[str] = "https://github.com/asdrubalivan/remote-venezuela-hiring"
OG_IMAGE_PATH: Final[str] = "/static/og.png"
OG_IMAGE_ALT: Final[str] = (
    "Remote Venezuela Hiring: directorio de empresas que contratan remoto desde Venezuela"
)

TITLE_MAX: Final[int] = 60
DESCRIPTION_MAX: Final[int] = 160

INDEX_TITLE: Final[str] = "Empresas que contratan venezolanos en remoto"
STATS_TITLE: Final[str] = "Estadísticas de empresas que contratan desde Venezuela"
NOT_FOUND_TITLE: Final[str] = "Página no encontrada"

# Tags that appear on too many companies (or only on one) say little about
# similarity, so they are ignored when picking related companies.
RELATED_MIN_TAG_COMPANIES: Final[int] = 2
RELATED_MAX_TAG_COMPANIES: Final[int] = 12
RELATED_LIMIT: Final[int] = 4

_WHITESPACE_RE: Final[re.Pattern[str]] = re.compile(r"\s+")


def site_url() -> str:
    """Return the canonical origin (no trailing slash); ``RVH_SITE_URL`` is for tests."""
    url = os.environ.get("RVH_SITE_URL", DEFAULT_SITE_URL)
    if not url.startswith("https://") or url.endswith("/"):
        msg = f"RVH_SITE_URL must start with https:// and not end with '/': {url!r}"
        raise ValueError(msg)
    return url


def normalize_text(text: str) -> str:
    """Collapse every run of whitespace (newlines included) into a single space."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def truncate(text: str, limit: int) -> str:
    """Cut *text* to at most *limit* characters at a word boundary, adding ``…``."""
    text = normalize_text(text)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.-—") + "…"


def duplicate_names(companies: Iterable[Company]) -> set[str]:
    """Lower-cased company names shared by more than one company."""
    counts = Counter(c.name.casefold() for c in companies)
    return {name for name, count in counts.items() if count > 1}


def display_name(company: Company, duplicates: set[str]) -> str:
    """The company name, disambiguated with its id when the name is not unique."""
    if company.name.casefold() in duplicates:
        return f"{company.name} ({company.id})"
    return company.name


def company_title(name: str) -> str:
    """Neutral question-style title, ``<= TITLE_MAX`` characters."""
    suffix = ": ¿contrata desde Venezuela?"
    branded = f"{name}{suffix} | {SITE_NAME}"
    if len(branded) <= TITLE_MAX:
        return branded
    plain = f"{name}{suffix}"
    if len(plain) <= TITLE_MAX:
        return plain
    return truncate(name, TITLE_MAX - len(suffix) - 1) + suffix


def _verified_clause(method_label: str, checked: str) -> str:
    return f"verificación: {method_label.lower()}, {checked}"


def company_summary(
    name: str, status: str, method_label: str, platform_label: str, checked: str
) -> str:
    """One neutral, community-attributed sentence about the company's stance."""
    if status == "accepts":
        stance = (
            f"Según información aportada por la comunidad, {name} probablemente acepta "
            "candidatos con residencia en Venezuela."
        )
    elif status == "rejects":
        stance = (
            f"La comunidad reporta que {name} no acepta candidatos con residencia en Venezuela."
        )
    else:
        stance = (
            f"Todavía no se ha confirmado si {name} acepta candidatos con residencia en Venezuela."
        )
    return (
        f"{stance} Método de verificación: {method_label.lower()}. "
        f"Plataforma de empleo: {platform_label}. Última verificación: {checked}."
    )


def company_description(
    name: str, status: str, method_label: str, checked: str, notes: str | None
) -> str:
    """Status-aware meta description (<= DESCRIPTION_MAX), enriched with the notes."""
    if status == "accepts":
        lead = f"{name} probablemente acepta candidatos desde Venezuela"
    elif status == "rejects":
        lead = f"{name} fue reportada como no aceptante de candidatos desde Venezuela"
    else:
        lead = f"Sin confirmar si {name} acepta candidatos desde Venezuela"
    text = f"{lead} ({_verified_clause(method_label, checked)})."
    if notes and normalize_text(notes):
        text = f"{text} {normalize_text(notes)}"
    return truncate(text, DESCRIPTION_MAX)


def index_description(total: int, accepts: int) -> str:
    return truncate(
        f"Directorio comunitario de {total} empresas que contratan remoto desde Venezuela: "
        f"{accepts} probablemente aceptan candidatos venezolanos. Filtra por plataforma, "
        "verificación y etiquetas.",
        DESCRIPTION_MAX,
    )


def stats_description(total: int, accepts_pct: int) -> str:
    return truncate(
        f"Estadísticas de {total} empresas activas: {accepts_pct}% probablemente acepta "
        "candidatos desde Venezuela. Distribución por método de verificación y plataforma.",
        DESCRIPTION_MAX,
    )


def related_companies(
    company: Company, companies: list[Company], limit: int = RELATED_LIMIT
) -> list[Company]:
    """Deterministic similar companies: shared informative tags, then platform.

    Excludes the company itself and archived entries (their pages are noindex).
    """
    tag_counts = Counter(tag for c in companies for tag in c.tags)
    informative = {
        tag
        for tag, count in tag_counts.items()
        if RELATED_MIN_TAG_COMPANIES <= count <= RELATED_MAX_TAG_COMPANIES
    }
    mine = set(company.tags) & informative

    def score(other: Company) -> tuple[int, int, int]:
        shared = len(mine & set(other.tags))
        same_platform = int(
            other.hiring_platform is not None and other.hiring_platform == company.hiring_platform
        )
        same_status = int(other.status == company.status)
        return (shared, same_platform, same_status)

    candidates = [c for c in companies if c.id != company.id and not c.archived]
    ranked = sorted(candidates, key=lambda c: (tuple(-s for s in score(c)), c.id))
    return [c for c in ranked if score(c)[0] > 0][:limit]


def website_json_ld(base: str) -> dict[str, object]:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "alternateName": SITE_ALTERNATE_NAME,
        "url": f"{base}/",
        "inLanguage": "es",
    }


def dataset_json_ld(base: str, total: int, date_modified: date) -> dict[str, object]:
    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Empresas que contratan (o no) desde Venezuela",
        "description": (
            f"Registro comunitario de {total} empresas y su postura hacia candidatos con "
            "residencia en Venezuela: estado, método de verificación, plataforma de empleo, "
            "etiquetas y fecha de la última verificación."
        ),
        "url": f"{base}/",
        "inLanguage": "es",
        "isAccessibleForFree": True,
        "dateModified": date_modified.isoformat(),
        "creator": {"@type": "Organization", "name": SITE_NAME, "url": GITHUB_URL},
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "application/json",
                "contentUrl": f"{base}/companies.json",
            }
        ],
    }


def robots_txt(base: str) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"


def sitemap_xml(entries: Iterable[tuple[str, date]]) -> str:
    """Render a sitemap from ``(absolute_url, lastmod)`` pairs (``loc`` + ``lastmod`` only)."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in entries:
        lines.append(
            f"  <url><loc>{escape(loc)}</loc><lastmod>{lastmod.isoformat()}</lastmod></url>"
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"
