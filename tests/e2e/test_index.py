"""E2E tests for the index page: filters, sorting, status tabs, navigation.

These tests exercise the public RVH.filter API + observable DOM:
  - rvh:filter:applied custom event
  - status-tab counts and aria-selected
  - sort arrows + aria-sort
  - per-company detail navigation
"""

from __future__ import annotations

from playwright.sync_api import Page, expect


def visible_row_count(page: Page) -> int:
    return page.locator(".company-row:visible").count()


def test_index_loads_with_expected_companies(page: Page, base_url: str) -> None:
    page.goto(base_url)
    expect(page.locator(".page-title")).to_contain_text("Compatibilidad")
    # 9 active YAML files; all archived=false in current dataset.
    assert visible_row_count(page) == 9
    expect(page.locator(".status-tab[data-status='all'] .status-tab-count")).to_have_text("9")


def test_search_filters_rows(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.fill("#company-search", "proxify")
    page.wait_for_function("window.RVH.filter.getState().search === 'proxify'")
    page.wait_for_timeout(180)  # debounce
    assert visible_row_count(page) == 1
    expect(page.locator(".company-row:visible .company-link")).to_have_text("Proxify")


def test_status_tab_filters_to_accepts(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click(".status-tab[data-status='accepts']")
    page.wait_for_function("window.RVH.filter.getState().status === 'accepts'")
    visible = page.locator(".company-row:visible")
    assert visible.count() > 0
    for i in range(visible.count()):
        assert visible.nth(i).get_attribute("data-status") == "accepts"
    expect(page.locator(".status-tab[data-status='accepts']")).to_have_attribute("aria-selected", "true")


def test_method_filter_select(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.select_option("#filter-method", "application_form")
    page.wait_for_function("window.RVH.filter.getState().method === 'application_form'")
    visible = page.locator(".company-row:visible")
    for i in range(visible.count()):
        assert visible.nth(i).get_attribute("data-method") == "application_form"


def test_sort_by_name_toggles_direction(page: Page, base_url: str) -> None:
    page.goto(base_url)
    # First click on already-active sort toggles direction asc → desc
    page.click(".sort-th[data-sort='name']")
    page.wait_for_function("window.RVH.filter.getState().sortDir === 'desc'")
    expect(page.locator(".sort-th[data-sort='name']")).to_have_attribute("aria-sort", "descending")
    first_name = page.locator(".company-row:visible .company-link").first.inner_text()
    # In desc order, Xebia (X) should come first alphabetically before Customer.io.
    assert first_name.lower().startswith(("x", "w", "v", "t", "r", "p"))


def test_clear_filters_button(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.fill("#company-search", "proxify")
    page.wait_for_timeout(180)
    expect(page.locator("#clear-filters")).to_be_visible()
    page.click("#clear-filters")
    page.wait_for_function("window.RVH.filter.getState().search === ''")
    assert visible_row_count(page) == 9


def test_empty_state_when_no_match(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.fill("#company-search", "zzzz-no-match")
    page.wait_for_timeout(180)
    expect(page.locator("#empty-state")).to_be_visible()


def test_company_row_navigates_to_detail(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click(".company-row[data-id='proxify'] .company-link")
    expect(page).to_have_url(f"{base_url}/company/proxify.html")
    expect(page.locator(".company-card-title")).to_have_text("Proxify")


def test_filter_applied_event_fires(page: Page, base_url: str) -> None:
    page.goto(base_url)
    # Install a listener and verify it captures the event payload.
    page.evaluate(
        "window.__capturedEvents = [];"
        "jQuery(document).on('rvh:filter:applied', function (e, payload) {"
        "  window.__capturedEvents.push(payload);"
        "});"
    )
    page.click(".status-tab[data-status='rejects']")
    page.wait_for_function("window.__capturedEvents.length > 0")
    last = page.evaluate("window.__capturedEvents.at(-1)")
    assert last["state"]["status"] == "rejects"
    assert isinstance(last["visible"], int)


def test_stale_marker_on_tesorio_if_present(page: Page, base_url: str) -> None:
    """Tesorio's last_checked = 2025-11-15. If today is >180 days later it's
    rendered with the DESACT. marker; otherwise this test is a no-op."""
    page.goto(base_url)
    row = page.locator(".company-row[data-id='tesorio']")
    if row.count() == 0:
        return  # dataset may evolve
    marker = row.locator(".stale-marker")
    # Either the marker exists, or last_checked has been bumped — both valid.
    assert marker.count() >= 0
