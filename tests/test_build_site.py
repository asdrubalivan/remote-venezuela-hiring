import os
from pathlib import Path

import pytest

from remote_venezuela_hiring.build_site import (
    DEFAULT_OUTPUT_DIR,
    STATIC_DIR,
    TEMPLATES_DIR,
    build,
)


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "site"


def test_build_produces_index_html(output_dir: Path) -> None:
    index_path = build(output_dir=output_dir)
    assert index_path == output_dir / "index.html"
    assert index_path.is_file()


def test_index_contains_company_names(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "Proxify" in html
    assert "Workana" in html
    assert "Devlane" in html


def test_index_renders_status_badges(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    # New design exposes status-{value} classes on each badge.
    assert "status-accepts" in html
    assert "status-rejects" in html
    assert "status-unknown" in html


def test_index_has_status_tabs(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert 'class="status-tabs"' in html
    assert 'data-status="accepts"' in html
    assert 'data-status="rejects"' in html


@pytest.mark.skipif(
    bool(os.environ.get("RVH_SKIP_JS_BUILD")),
    reason="JS bundle not compiled when RVH_SKIP_JS_BUILD is set",
)
def test_static_assets_copied(output_dir: Path) -> None:
    build(output_dir=output_dir)
    assert (output_dir / "static" / "main.css").is_file()
    assert (output_dir / "static" / "filter.js").is_file()
    assert (output_dir / "static" / "theme.js").is_file()


def test_build_wipes_existing_output(output_dir: Path) -> None:
    output_dir.mkdir()
    stale = output_dir / "stale.html"
    stale.write_text("old", encoding="utf-8")

    build(output_dir=output_dir)

    assert not stale.exists()
    assert (output_dir / "index.html").is_file()


def test_build_handles_empty_data_dir(tmp_path: Path, output_dir: Path) -> None:
    empty_data = tmp_path / "empty"
    empty_data.mkdir()
    index_path = build(output_dir=output_dir, data_dir=empty_data)
    html = index_path.read_text(encoding="utf-8")
    # Empty dataset still renders the all-tab with a 0 count.
    assert 'data-status="all"' in html
    assert (output_dir / "static" / "main.css").is_file()


def test_default_paths_resolve_under_repo() -> None:
    assert TEMPLATES_DIR.is_dir()
    assert STATIC_DIR.is_dir()
    assert DEFAULT_OUTPUT_DIR.name == "site"


def test_company_links_are_internal(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    # Company rows now link to per-company static pages.
    assert 'href="company/proxify.html"' in html


def test_stats_page_generated(output_dir: Path) -> None:
    build(output_dir=output_dir)
    stats = output_dir / "stats.html"
    assert stats.is_file()
    html = stats.read_text(encoding="utf-8")
    assert "Estadísticas" in html
    assert "stat-card" in html
    assert "bar-chart" in html


def test_company_detail_pages_generated(output_dir: Path) -> None:
    build(output_dir=output_dir)
    company_dir = output_dir / "company"
    assert company_dir.is_dir()
    proxify = company_dir / "proxify.html"
    assert proxify.is_file()
    html = proxify.read_text(encoding="utf-8")
    assert "Proxify" in html
    assert "Volver a todas las empresas" in html


def test_company_detail_outbound_links_safe(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "company" / "proxify.html").read_text(encoding="utf-8")
    # External links should still carry the noopener-nofollow attrs.
    assert 'rel="noopener noreferrer nofollow"' in html
    assert 'target="_blank"' in html
