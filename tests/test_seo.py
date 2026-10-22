"""Unit tests for the pure SEO helpers."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import date
from typing import TYPE_CHECKING

import pytest

from remote_venezuela_hiring import seo
from remote_venezuela_hiring.build_site import build
from remote_venezuela_hiring.models import Company

if TYPE_CHECKING:
    from pathlib import Path


def _company(
    cid: str,
    name: str | None = None,
    *,
    tags: list[str] | None = None,
    status: str = "accepts",
    archived: bool = False,
    platform: str | None = None,
) -> Company:
    return Company.model_validate(
        {
            "id": cid,
            "name": name or cid.title(),
            "website": f"https://{cid}.example",
            "status": status,
            "last_checked": "2026-01-01",
            "verification_method": "public_job_post",
            "hiring_platform": platform,
            "tags": tags or [],
            "archived": archived,
        }
    )


def test_site_url_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RVH_SITE_URL", raising=False)
    assert seo.site_url() == "https://contrataenve.com"


@pytest.mark.parametrize("bad", ["http://x.example", "https://x.example/", "x.example"])
def test_site_url_rejects_invalid_override(monkeypatch: pytest.MonkeyPatch, bad: str) -> None:
    monkeypatch.setenv("RVH_SITE_URL", bad)
    with pytest.raises(ValueError, match="RVH_SITE_URL"):
        seo.site_url()


def test_truncate_cuts_at_word_boundary() -> None:
    out = seo.truncate("uno dos tres cuatro cinco", 14)
    assert out == "uno dos tres…"
    assert len(out) <= 14


def test_truncate_keeps_short_text_and_normalizes_whitespace() -> None:
    assert seo.truncate("hola\n  mundo \n", 50) == "hola mundo"


@pytest.mark.parametrize(
    "name",
    ["A", "Allied Global Technology Services", "X" * 120, "Ñandú Compañía de Tecnología Avanzada"],
)
def test_company_title_never_exceeds_limit(name: str) -> None:
    title = seo.company_title(name)
    assert len(title) <= seo.TITLE_MAX
    assert "¿contrata desde Venezuela?" in title


def test_company_title_keeps_brand_when_it_fits() -> None:
    assert seo.company_title("Acme").endswith(f"| {seo.SITE_NAME}")


def test_company_description_is_neutral_and_bounded() -> None:
    long_notes = "Texto muy largo. " * 40
    for status in ("accepts", "rejects", "unknown"):
        text = seo.company_description("Acme", status, "Oferta pública", "5 ago 2026", long_notes)
        assert len(text) <= seo.DESCRIPTION_MAX
        assert "\n" not in text
    rejects = seo.company_description("Acme", "rejects", "Oferta pública", "5 ago 2026", None)
    assert "reportada" in rejects
    assert "no contrata" not in rejects


def test_company_description_normalizes_notes_newlines() -> None:
    text = seo.company_description("Acme", "accepts", "Reclutador/a", "1 ene 2026", "Una.\nDos.\n")
    assert "\n" not in text
    assert "Una. Dos." in text


def test_duplicate_names_are_disambiguated_with_id() -> None:
    a, b, c = _company("mercury-1", "Mercury"), _company("mercury-2", "mercury"), _company("zed")
    dups = seo.duplicate_names([a, b, c])
    assert seo.display_name(a, dups) == "Mercury (mercury-1)"
    assert seo.display_name(c, dups) == "Zed"


def test_related_companies_rules() -> None:
    me = _company("me", tags=["python", "fintech", "remote"], platform="greenhouse")
    close = _company("close", tags=["python", "fintech"], platform="greenhouse")
    far = _company("far", tags=["python"])
    archived = _company("archived", tags=["python", "fintech"], archived=True)
    unrelated = _company("unrelated", tags=["java", "java-too"])
    pool = [me, close, far, archived, unrelated]
    related = seo.related_companies(me, pool)
    ids = [c.id for c in related]
    assert ids == ["close", "far"]
    assert "me" not in ids
    assert "archived" not in ids


def test_related_companies_ignores_tags_shared_by_too_many_companies() -> None:
    crowd = [
        _company(f"c{i:02d}", tags=["remote"]) for i in range(seo.RELATED_MAX_TAG_COMPANIES + 1)
    ]
    assert seo.related_companies(crowd[0], crowd) == []


def test_related_companies_is_deterministic_with_id_tiebreak() -> None:
    me = _company("me", tags=["python"])
    pool = [me, _company("b", tags=["python"]), _company("a", tags=["python"])]
    assert [c.id for c in seo.related_companies(me, pool)] == ["a", "b"]


def test_sitemap_is_valid_xml_and_escapes() -> None:
    xml = seo.sitemap_xml([("https://x.example/a?b=1&c=2", date(2026, 1, 2))])
    root = ET.fromstring(xml)  # noqa: S314 - parsing our own output
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    assert root.find("s:url/s:loc", ns).text == "https://x.example/a?b=1&c=2"  # type: ignore[union-attr]
    assert root.find("s:url/s:lastmod", ns).text == "2026-01-02"  # type: ignore[union-attr]
    assert xml.startswith('<?xml version="1.0" encoding="UTF-8"?>')


def test_robots_txt_declares_sitemap_and_blocks_nothing() -> None:
    text = seo.robots_txt("https://x.example")
    assert "Sitemap: https://x.example/sitemap.xml" in text
    assert "Disallow" not in text


def test_dataset_json_ld_has_no_license_claim() -> None:
    data = seo.dataset_json_ld("https://x.example", 3, date(2026, 1, 2))
    assert data["@type"] == "Dataset"
    assert "license" not in data
    assert len(str(data["description"])) > 50


def test_site_url_env_override_used_by_build(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("RVH_SITE_URL", "https://staging.example")
    build(output_dir=tmp_path / "site")
    assert "https://staging.example/" in (tmp_path / "site" / "index.html").read_text("utf-8")
