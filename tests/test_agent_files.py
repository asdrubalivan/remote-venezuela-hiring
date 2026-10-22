"""Files for AI agents: Markdown pages, llms.txt, agents.txt/json and robots.txt bot rules."""

from __future__ import annotations

import json
import re
from datetime import date
from typing import TYPE_CHECKING

import pytest

from remote_venezuela_hiring import agent_files, seo
from remote_venezuela_hiring.build_site import LABELS, build
from remote_venezuela_hiring.models import STALE_AFTER_DAYS, Company, today_utc

if TYPE_CHECKING:
    from pathlib import Path

BASE = "https://x.example"


def _company(**overrides: object) -> Company:
    data: dict[str, object] = {
        "id": "acme",
        "name": "Acme",
        "website": "https://acme.example",
        "status": "accepts",
        "last_checked": today_utc(),
        "verification_method": "public_job_post",
        "hiring_platform": "greenhouse",
        "tags": ["saas"],
        "notes": "Oferta abierta a LATAM.",
    }
    data.update(overrides)
    return Company.model_validate(data)


def _yaml(company_id: str, *, status: str = "accepts", archived: bool = False) -> str:
    return (
        f"id: {company_id}\nname: {company_id.title()}\nwebsite: https://{company_id}.example\n"
        f"status: {status}\nlast_checked: 2026-01-02\nverification_method: public_job_post\n"
        f"archived: {str(archived).lower()}\n"
    )


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root: Path = tmp_path_factory.mktemp("agent-files")
    data = root / "companies"
    data.mkdir()
    (data / "alpha.yaml").write_text(_yaml("alpha"), encoding="utf-8")
    (data / "beta.yaml").write_text(_yaml("beta", status="rejects"), encoding="utf-8")
    (data / "gone.yaml").write_text(_yaml("gone", archived=True), encoding="utf-8")
    out = root / "site"
    build(output_dir=out, data_dir=data)
    return out


# ── robots.txt ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "bot",
    ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User"],
)
def test_robots_txt_names_each_ai_bot_and_allows_it(bot: str) -> None:
    text = seo.robots_txt(BASE)
    groups = [g for g in text.split("\n\n") if f"User-agent: {bot}" in g]
    assert len(groups) == 1
    assert "Allow: /" in groups[0]
    assert "Disallow" not in text


# ── Markdown pages ─────────────────────────────────────────────────────


def test_company_markdown_has_facts_links_and_freshness() -> None:
    company = _company()
    md = agent_files.company_markdown(
        company,
        base=BASE,
        name="Acme",
        labels=LABELS,
        summary="Resumen. Verificada hoy.",
        related=[_company(id="other", name="Other")],
    )
    assert md.startswith("# Acme: ¿contrata desde Venezuela?\n")
    assert "> Resumen. Verificada hoy." in md
    assert "- Estado: Probablemente acepta Venezuela (`accepts`)" in md
    assert f"- Última verificación: {company.last_checked.isoformat()}\n" in md
    assert "- Etiquetas: saas" in md
    assert "Oferta abierta a LATAM." in md
    assert f"[Other]({BASE}/company/other.md)" in md
    assert f"{BASE}/company/acme.html" in md
    assert "licencia MIT" in md


def test_company_markdown_marks_stale_entries() -> None:
    old = date(2020, 1, 1)
    md = agent_files.company_markdown(
        _company(last_checked=old), base=BASE, name="Acme", labels=LABELS, summary="s", related=[]
    )
    assert f"- Última verificación: {old.isoformat()} (desactualizada)" in md


@pytest.mark.parametrize(
    ("age", "stale", "expected"),
    [
        (0, False, "Verificada hoy."),
        (1, False, "Verificada hace 1 día."),
        (30, False, "Verificada hace 30 días."),
        (400, True, f"más de {STALE_AFTER_DAYS})"),
    ],
)
def test_freshness_sentence(age: int, *, stale: bool, expected: str) -> None:
    assert expected in agent_files.freshness_sentence(age, stale=stale)


def test_index_markdown_has_no_truncated_summary_or_bare_trailing_url() -> None:
    md = agent_files.index_markdown(
        [_company()], base=BASE, labels=LABELS, last_modified=date(2026, 1, 2)
    )
    assert "…" not in md
    assert f"[llms.txt]({BASE}/llms.txt)" in md
    assert f"{BASE}/llms.txt." not in md


def test_markdown_link_text_cannot_break_the_link() -> None:
    md = agent_files.index_markdown(
        [_company(name="Bad [name]")], base=BASE, labels=LABELS, last_modified=date(2026, 1, 2)
    )
    assert "[Bad (name)](https://x.example/company/acme.md)" in md


# ── llms.txt ───────────────────────────────────────────────────────────


def test_llms_txt_follows_the_llmstxt_format() -> None:
    text = agent_files.llms_txt(
        [_company(), _company(id="beta", name="Beta", status="rejects")],
        base=BASE,
        labels=LABELS,
        last_modified=date(2026, 1, 2),
    )
    lines = text.splitlines()
    assert lines[0] == "# Remote Venezuela Hiring"
    assert lines[2].startswith("> ")
    assert sum(1 for line in lines if line.startswith("# ")) == 1
    assert [line for line in lines if line.startswith("## ")][-1] == "## Optional"
    assert f"- [Acme]({BASE}/company/acme.md): Greenhouse · verificada" in text
    assert f"- [Dataset completo]({BASE}/companies.json)" in text


def test_llms_txt_excludes_archived_companies() -> None:
    text = agent_files.llms_txt(
        [_company(), _company(id="gone", name="Gone", archived=True)],
        base=BASE,
        labels=LABELS,
        last_modified=date(2026, 1, 2),
    )
    assert "Gone" not in text


# ── agents.txt / agents.json ───────────────────────────────────────────

_DIRECTIVE_RE = re.compile(r"^WebMCP: https://\S+$")


def test_agents_txt_has_only_comments_and_known_directives() -> None:
    lines = agent_files.agents_txt(BASE).splitlines()
    assert lines[:3] == [
        "# agents.txt",
        "# Standard: https://agents-txt.com",
        f"# JSON: {BASE}/agents.json",
    ]
    for line in lines:
        assert not line or line.startswith("#") or _DIRECTIVE_RE.match(line), line
    assert f"WebMCP: {BASE}/" in lines


def test_agents_json_matches_the_v1_schema_shape() -> None:
    data = json.loads(agent_files.agents_json(BASE))
    assert set(data) <= {"$schema", "version", "standard", "site", "webmcp"}
    assert {"version", "standard", "site"} <= set(data)
    assert re.fullmatch(r"\d+\.\d+", data["version"])
    assert data["standard"].startswith("https://")
    assert set(data["site"]) <= {"name", "url", "description"}
    assert data["site"]["name"]
    assert data["site"]["url"].startswith("https://")
    for entry in data["webmcp"]:
        assert set(entry) <= {"url", "description"}
        assert entry["url"].startswith("https://")


# ── built site ─────────────────────────────────────────────────────────


def test_build_writes_markdown_only_for_active_companies(site: Path) -> None:
    assert (site / "company" / "alpha.md").is_file()
    assert (site / "company" / "beta.md").is_file()
    assert not (site / "company" / "gone.md").exists()
    assert (site / "company" / "gone.html").is_file()
    assert (site / "index.md").is_file()


def test_build_writes_agent_files(site: Path) -> None:
    for name in ("llms.txt", "agents.txt", "agents.json", "robots.txt"):
        assert (site / name).is_file(), name
    assert "company/alpha.md" in (site / "llms.txt").read_text(encoding="utf-8")
    assert "company/alpha.md" in (site / "index.md").read_text(encoding="utf-8")


def test_html_pages_link_their_markdown_version_and_llms_txt(site: Path) -> None:
    alpha = (site / "company" / "alpha.html").read_text(encoding="utf-8")
    assert (
        '<link rel="alternate" type="text/markdown" href="https://contrataenve.com/company/alpha.md"'
        in alpha
    )
    assert 'rel="describedby"' in alpha
    assert "https://contrataenve.com/llms.txt" in alpha
    index = (site / "index.html").read_text(encoding="utf-8")
    assert 'type="text/markdown" href="https://contrataenve.com/index.md"' in index
    gone = (site / "company" / "gone.html").read_text(encoding="utf-8")
    assert 'type="text/markdown"' not in gone


def test_company_page_states_how_fresh_the_verification_is(site: Path) -> None:
    html = (site / "company" / "alpha.html").read_text(encoding="utf-8")
    # The fixture's 2026-01-02 verification is long past the stale threshold.
    assert "Esta entrada está desactualizada: se verificó por última vez hace" in html
