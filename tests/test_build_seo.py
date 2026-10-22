"""Integration tests: the built site carries consistent SEO markup."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from typing import TYPE_CHECKING

import pytest

from remote_venezuela_hiring.build_site import build
from remote_venezuela_hiring.seo import DESCRIPTION_MAX, TITLE_MAX

BASE = "https://contrataenve.com"
if TYPE_CHECKING:
    from pathlib import Path

NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out: Path = tmp_path_factory.mktemp("seo-site") / "site"
    build(output_dir=out)
    return out


class _Head(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.metas: dict[str, str] = {}
        self.title = ""
        self._in_title = False
        self.jsonld: list[str] = []
        self._in_ld = False
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a["href"])
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.metas[key] = a.get("content", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self.jsonld.append("")
        elif tag == "a" and "href" in a:
            self.hrefs.append(a["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            self._in_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        elif self._in_ld:
            self.jsonld[-1] += data


def _parse(path: Path) -> _Head:
    head = _Head()
    head.feed(path.read_text(encoding="utf-8"))
    return head


def _pages(site: Path) -> list[Path]:
    return sorted(
        p for p in [site / "index.html", site / "stats.html", *(site / "company").glob("*.html")]
    )


def test_every_page_has_one_absolute_https_canonical(site: Path) -> None:
    seen: set[str] = set()
    for page in _pages(site):
        head = _parse(page)
        assert len(head.canonicals) == 1, page
        canonical = head.canonicals[0]
        assert canonical.startswith(BASE + "/"), page
        assert canonical not in seen, f"duplicate canonical {canonical}"
        seen.add(canonical)
        assert head.metas["og:url"] == canonical


def test_canonical_urls_match_page_paths(site: Path) -> None:
    assert _parse(site / "index.html").canonicals == [f"{BASE}/"]
    assert _parse(site / "stats.html").canonicals == [f"{BASE}/stats.html"]
    assert _parse(site / "company" / "a-team.html").canonicals == [f"{BASE}/company/a-team.html"]


def test_titles_and_descriptions_are_bounded_and_company_ones_unique(site: Path) -> None:
    titles: set[str] = set()
    descriptions: set[str] = set()
    for page in (site / "company").glob("*.html"):
        head = _parse(page)
        title, desc = head.title.strip(), head.metas["description"]
        assert 0 < len(title) <= TITLE_MAX, page
        assert 0 < len(desc) <= DESCRIPTION_MAX, page
        titles.add(title)
        descriptions.add(desc)
    n = len(list((site / "company").glob("*.html")))
    assert len(titles) == n
    assert len(descriptions) == n


def test_social_tags_present(site: Path) -> None:
    head = _parse(site / "index.html")
    assert head.metas["og:locale"] == "es_VE"
    assert head.metas["twitter:card"] == "summary_large_image"
    assert head.metas["og:image"] == f"{BASE}/static/og.png"
    assert head.metas["twitter:image"] == f"{BASE}/static/og.png"


def test_sitemap_matches_indexable_pages_exactly(site: Path) -> None:
    root = ET.parse(site / "sitemap.xml").getroot()  # noqa: S314 - our own output
    locs = {e.text for e in root.findall("s:url/s:loc", NS)}
    indexable = set()
    for page in [*_pages(site), site / "404.html"]:
        head = _parse(page)
        if "noindex" in head.metas.get("robots", "") or not head.canonicals:
            continue
        indexable.add(head.canonicals[0])
    assert locs == indexable
    assert f"{BASE}/index.html" not in locs
    for loc in locs:
        assert loc is not None
        path = loc.removeprefix(BASE) or "/"
        target = site / "index.html" if path == "/" else site / path.lstrip("/")
        assert target.is_file(), loc
    for lastmod in root.findall("s:url/s:lastmod", NS):
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod.text or "")


def test_robots_txt(site: Path) -> None:
    text = (site / "robots.txt").read_text(encoding="utf-8")
    assert f"Sitemap: {BASE}/sitemap.xml" in text
    assert "Disallow" not in text


def test_404_page_uses_absolute_urls_and_noindex(site: Path) -> None:
    head = _parse(site / "404.html")
    assert head.canonicals == []
    assert "og:url" not in head.metas
    assert head.metas["robots"] == "noindex, follow"
    html = (site / "404.html").read_text(encoding="utf-8")
    assert 'href="/static/main.css"' in html
    assert 'src="/static/theme.js"' in html
    assert 'href="/"' in html


def test_internal_links_do_not_point_to_index_html(site: Path) -> None:
    for page in _pages(site):
        for href in _parse(page).hrefs:
            assert not href.endswith("index.html"), (page, href)


def test_root_icons_exist_and_sourcemaps_are_not_published(site: Path) -> None:
    assert (site / "favicon.ico").is_file()
    assert (site / "apple-touch-icon.png").is_file()
    assert (site / "static" / "favicon.svg").is_file()
    assert (site / "static" / "og.png").is_file()
    assert not list((site / "static").glob("*.map"))
    assert (site / "CNAME").read_text(encoding="utf-8").strip() == "contrataenve.com"


def test_json_ld_is_valid_and_scoped(site: Path) -> None:
    index = _parse(site / "index.html")
    blocks = [json.loads(b) for b in index.jsonld]
    assert {b["@type"] for b in blocks} == {"WebSite", "Dataset"}
    website = next(b for b in blocks if b["@type"] == "WebSite")
    assert website["url"] == f"{BASE}/"
    assert "potentialAction" not in website
    dataset = next(b for b in blocks if b["@type"] == "Dataset")
    assert dataset["distribution"][0]["contentUrl"] == f"{BASE}/companies.json"
    assert _parse(next((site / "company").glob("*.html"))).jsonld == []


def test_index_has_guide_after_table_and_json_alternate(site: Path) -> None:
    html = (site / "index.html").read_text(encoding="utf-8")
    assert 'id="como-leer"' in html
    assert html.index('id="company-tray"') < html.index('id="como-leer"')
    assert html.index('id="como-leer"') < html.index("page-footer-links")
    assert 'rel="alternate" type="application/json"' in html


def test_company_pages_have_summary_and_never_link_to_themselves(site: Path) -> None:
    for page in (site / "company").glob("*.html"):
        html = page.read_text(encoding="utf-8")
        assert 'class="company-summary"' in html
        related_block = html.partition('class="related"')[2].partition("</section>")[0]
        assert f'href="{page.name}"' not in related_block
        for href in re.findall(r'href="([^"]+\.html)"', related_block):
            assert (site / "company" / href).is_file(), (page, href)


def _write_company(data_dir: Path, cid: str, name: str, extra: str = "") -> None:
    (data_dir / f"{cid}.yaml").write_text(
        f"id: {cid}\nname: {name}\nwebsite: https://{cid}.example\nstatus: accepts\n"
        f"last_checked: 2026-01-01\nverification_method: public_job_post\n{extra}",
        encoding="utf-8",
    )


def test_archived_company_is_noindex_and_not_in_sitemap(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_company(data_dir, "live", "Live")
    _write_company(data_dir, "gone", "Gone", "archived: true\n")
    out = tmp_path / "site"
    build(output_dir=out, data_dir=data_dir)
    assert _parse(out / "company" / "gone.html").metas["robots"] == "noindex, follow"
    assert "robots" not in _parse(out / "company" / "live.html").metas
    sitemap = (out / "sitemap.xml").read_text(encoding="utf-8")
    assert "company/live.html" in sitemap
    assert "company/gone.html" not in sitemap


def test_hostile_company_name_cannot_break_out_of_json_ld_or_html(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_company(data_dir, "evil", '"</script><b>x</b>"')
    out = tmp_path / "site"
    build(output_dir=out, data_dir=data_dir)
    for page in (out / "index.html", out / "company" / "evil.html"):
        html = page.read_text(encoding="utf-8")
        assert "</script><b>" not in html
        for block in _parse(page).jsonld:
            json.loads(block)


def test_duplicate_names_get_unique_titles(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_company(data_dir, "mercury-1", "Mercury")
    _write_company(data_dir, "mercury-2", "Mercury")
    out = tmp_path / "site"
    build(output_dir=out, data_dir=data_dir)
    titles = {_parse(p).title for p in (out / "company").glob("*.html")}
    assert len(titles) == 2


def test_empty_data_dir_still_builds_sitemap(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    out = tmp_path / "site"
    build(output_dir=out, data_dir=data_dir)
    root = ET.parse(out / "sitemap.xml").getroot()  # noqa: S314
    assert len(root.findall("s:url", NS)) == 2


def test_long_names_that_collide_after_truncation_get_unique_titles(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    long_name = "Zeta Tecnologías Globales de Consultoría"
    _write_company(data_dir, "long-one", long_name + " Uno")
    _write_company(data_dir, "long-two", long_name + " Dos")
    out = tmp_path / "site"
    build(output_dir=out, data_dir=data_dir)
    titles = [_parse(p).title.strip() for p in (out / "company").glob("*.html")]
    assert len(set(titles)) == 2
    assert all(len(t) <= TITLE_MAX for t in titles)


def test_dataset_counts_only_active_companies(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_company(data_dir, "live", "Live")
    _write_company(data_dir, "gone", "Gone", "archived: true\n")
    out = tmp_path / "site"
    build(output_dir=out, data_dir=data_dir)
    dataset = next(
        b for b in map(json.loads, _parse(out / "index.html").jsonld) if b["@type"] == "Dataset"
    )
    assert "1 empresas" in dataset["description"]
