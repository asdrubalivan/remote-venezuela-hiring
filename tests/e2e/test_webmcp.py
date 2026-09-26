"""E2E tests for the WebMCP tools exposed by every page.

Chromium in Playwright has no native WebMCP, so an init script injects a fake
``document.modelContext`` that records registered tools; tests then call each
tool's ``execute`` exactly like an agent would.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pathlib import Path

    from playwright.sync_api import ConsoleMessage, Page

FAKE_MODEL_CONTEXT = """
window.__tools = {};
document.modelContext = {
  registerTool(tool) {
    window.__tools[tool.name] = tool;
    return Promise.resolve();
  },
};
"""

FAILING_MODEL_CONTEXT = """
document.modelContext = {
  registerTool() {
    return Promise.reject(new Error("boom"));
  },
};
"""

ALL_FIELDS = {
    "id",
    "name",
    "website",
    "status",
    "last_checked",
    "verification_method",
    "hiring_platform",
    "tags",
    "notes",
    "archived",
}


def _open_with_webmcp(page: Page, url: str) -> None:
    page.add_init_script(FAKE_MODEL_CONTEXT)
    page.goto(url)
    page.wait_for_function("Boolean(window.__tools.list_companies)")


def _call(page: Page, tool: str, args: dict[str, object] | None = None) -> dict[str, object]:
    """Invoke a registered tool and return the parsed JSON text of its result."""
    result = page.evaluate(
        "async ([name, args]) => window.__tools[name].execute(args, {})", [tool, args or {}]
    )
    assert result["content"][0]["type"] == "text"
    return cast("dict[str, object]", json.loads(result["content"][0]["text"]))


def _published(site_dir: Path) -> list[dict[str, object]]:
    data = json.loads((site_dir / "companies.json").read_text(encoding="utf-8"))
    return cast("list[dict[str, object]]", data["companies"])


def test_registers_list_companies_tool(page: Page, base_url: str) -> None:
    _open_with_webmcp(page, base_url)
    assert page.evaluate("Object.keys(window.__tools)") == ["list_companies"]
    tool = page.evaluate("window.__tools.list_companies")
    assert tool["name"] == "list_companies"
    assert "notes" in tool["description"]
    assert "Spanish" in tool["description"]


def test_list_companies_is_read_only_and_untrusted(page: Page, base_url: str) -> None:
    _open_with_webmcp(page, base_url)
    annotations = page.evaluate("window.__tools.list_companies.annotations")
    assert annotations["readOnlyHint"] is True
    assert annotations["untrustedContentHint"] is True


def test_list_returns_non_archived_companies_sorted_by_name(
    page: Page, base_url: str, site_dir: Path
) -> None:
    expected = [c["id"] for c in _published(site_dir) if not c["archived"]]
    _open_with_webmcp(page, base_url)
    result = _call(page, "list_companies")
    companies = cast("list[dict[str, object]]", result["companies"])
    assert result["count"] == len(expected) == len(companies)
    assert [c["id"] for c in companies] == expected
    assert all(c["archived"] is False for c in companies)


def test_list_returns_all_ten_fields_by_default(page: Page, base_url: str) -> None:
    _open_with_webmcp(page, base_url)
    companies = cast("list[dict[str, object]]", _call(page, "list_companies")["companies"])
    assert all(set(c) == ALL_FIELDS for c in companies)


def test_fields_limits_output_and_always_keeps_id(page: Page, base_url: str) -> None:
    _open_with_webmcp(page, base_url)
    companies = cast(
        "list[dict[str, object]]",
        _call(page, "list_companies", {"fields": ["name", "status"]})["companies"],
    )
    assert companies
    assert all(set(c) == {"id", "name", "status"} for c in companies)


def test_tools_work_from_company_detail_page(page: Page, base_url: str) -> None:
    _open_with_webmcp(page, f"{base_url}/company/toptal.html")
    result = _call(page, "list_companies", {"fields": ["name"]})
    names = [c["name"] for c in cast("list[dict[str, object]]", result["companies"])]
    assert "Toptal" in names


def test_no_errors_without_webmcp(page: Page, base_url: str) -> None:
    errors: list[str] = []

    def on_console(msg: ConsoleMessage) -> None:
        if msg.type == "error":
            errors.append(msg.text)

    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("console", on_console)
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    assert page.evaluate("'modelContext' in document") is False
    assert errors == []


def test_register_failure_only_warns(page: Page, base_url: str) -> None:
    warnings: list[str] = []
    errors: list[str] = []

    def on_console(msg: ConsoleMessage) -> None:
        if msg.type == "warning":
            warnings.append(msg.text)

    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("console", on_console)
    page.add_init_script(FAILING_MODEL_CONTEXT)
    page.goto(base_url)
    page.wait_for_function("true")
    page.wait_for_timeout(300)
    assert errors == []
    assert any("list_companies" in w for w in warnings)
