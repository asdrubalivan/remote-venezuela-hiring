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
    # At least the well-known sample entries should appear.
    assert "Proxify" in html
    assert "Workana" in html
    assert "Devlane" in html


def test_index_renders_status_badges(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "badge-accepts" in html
    assert "badge-rejects" in html
    assert "badge-unknown" in html


def test_index_has_summary_counts(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert 'class="summary-list"' in html
    assert 'class="summary-accepts"' in html or "summary-accepts" in html


def test_static_assets_copied(output_dir: Path) -> None:
    build(output_dir=output_dir)
    assert (output_dir / "static" / "main.css").is_file()
    assert (output_dir / "static" / "filter.js").is_file()


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
    assert ">0<" in html  # total count of 0
    assert (output_dir / "static" / "main.css").is_file()


def test_default_paths_resolve_under_repo() -> None:
    # Sanity-check that the module-level defaults point at real folders.
    assert TEMPLATES_DIR.is_dir()
    assert STATIC_DIR.is_dir()
    assert DEFAULT_OUTPUT_DIR.name == "site"


def test_index_links_are_safe(output_dir: Path) -> None:
    build(output_dir=output_dir)
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    # Every outbound company link should be rel='noopener nofollow' target='_blank'.
    assert 'rel="noopener nofollow"' in html
    assert 'target="_blank"' in html
