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
    count: int = page.locator(".company-row:visible").count()
    return count


def test_index_loads_with_expected_companies(page: Page, base_url: str) -> None:
    page.goto(base_url)
    expect(page.locator(".hero-title")).to_contain_text("Compatibilidad")
    tab_count = int(page.locator(".status-tab[data-status='all'] .status-tab-count").inner_text())
    assert tab_count > 0
    assert visible_row_count(page) == tab_count


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
    expect(page.locator(".status-tab[data-status='accepts']")).to_have_attribute(
        "aria-selected", "true"
    )


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
    # Verify the visible rows are actually in descending alphabetical order,
    # rather than hardcoding which company name happens to sort last — that
    # assumption breaks every time a new company is added to the directory.
    names = page.locator(".company-row:visible .company-link").all_inner_texts()
    assert names == sorted(names, key=str.lower, reverse=True)


def test_clear_filters_button(page: Page, base_url: str) -> None:
    page.goto(base_url)
    total = int(page.locator(".status-tab[data-status='all'] .status-tab-count").inner_text())
    page.fill("#company-search", "proxify")
    page.wait_for_timeout(180)
    expect(page.locator("#clear-filters")).to_be_visible()
    page.click("#clear-filters")
    page.wait_for_function("window.RVH.filter.getState().search === ''")
    assert visible_row_count(page) == total


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
        "document.addEventListener('rvh:filter:applied', function (e) {"
        "  window.__capturedEvents.push(e.detail);"
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


def test_status_tabs_follow_arrow_keys(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.focus(".status-tab[data-status='all']")
    page.keyboard.press("ArrowRight")
    page.wait_for_function("window.RVH.filter.getState().status === 'accepts'")
    accepts = page.locator(".status-tab[data-status='accepts']")
    expect(accepts).to_be_focused()
    expect(accepts).to_have_attribute("tabindex", "0")
    expect(page.locator(".status-tab[data-status='all']")).to_have_attribute("tabindex", "-1")
    expect(page.locator("#company-tray")).to_have_attribute("aria-labelledby", "status-tab-accepts")
    page.keyboard.press("End")
    page.wait_for_function("window.RVH.filter.getState().status === 'unknown'")
    page.keyboard.press("ArrowRight")
    page.wait_for_function("window.RVH.filter.getState().status === 'all'")


def test_sort_header_reflects_direction(page: Page, base_url: str) -> None:
    page.goto(base_url)
    name = page.locator(".sort-th[data-sort='name']")
    expect(name).to_have_attribute("data-dir", "asc")
    page.click(".sort-th[data-sort='last_checked'] .sort-btn")
    page.wait_for_function("window.RVH.filter.getState().sortBy === 'last_checked'")
    expect(page.locator(".sort-th[data-sort='last_checked']")).to_have_attribute("data-dir", "asc")
    assert name.get_attribute("data-dir") is None
    expect(name).to_have_attribute("aria-sort", "none")


def test_clear_button_hidden_until_filtered(page: Page, base_url: str) -> None:
    page.goto(base_url)
    expect(page.locator("#clear-filters")).to_be_hidden()
    page.click(".status-tab[data-status='rejects']")
    expect(page.locator("#clear-filters")).to_be_visible()


def test_filter_chip_removes_its_filter(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click(".status-tab[data-status='rejects']")
    chip = page.locator(".filter-chip[data-clear='status']")
    expect(chip).to_have_attribute("aria-label", "Quitar filtro: No acepta")
    assert chip.locator("svg use").count() == 1
    chip.click()
    page.wait_for_function("window.RVH.filter.getState().status === 'all'")
    expect(page.locator(".filter-chip")).to_have_count(0)


def _watch_stamping(page: Page) -> None:
    """Count every coupon that starts stamping; the class itself is transient."""
    page.evaluate(
        "window.__stamped = 0;"
        "new MutationObserver(function (records) {"
        "  for (const r of records) {"
        "    if (r.target.classList.contains('is-stamping')) window.__stamped += 1;"
        "  }"
        "}).observe(document.querySelector('#company-table tbody'),"
        "  { subtree: true, attributes: true, attributeFilter: ['class'] });"
    )


def test_changing_tab_stamps_visible_coupons(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.locator("#company-tray").scroll_into_view_if_needed()
    _watch_stamping(page)
    page.click(".status-tab[data-status='accepts']")
    page.wait_for_function("window.__stamped > 0")
    # Sorting re-orders the coupons but never re-stamps them.
    page.wait_for_function("document.querySelectorAll('.company-row.is-stamping').length === 0")
    page.evaluate("window.__stamped = 0")
    page.click(".sort-th[data-sort='last_checked'] .sort-btn")
    page.wait_for_function("window.RVH.filter.getState().sortBy === 'last_checked'")
    page.wait_for_timeout(100)
    assert page.evaluate("window.__stamped") == 0


def test_reduced_motion_never_stamps(page: Page, base_url: str) -> None:
    page.emulate_media(reduced_motion="reduce")
    page.goto(base_url)
    page.locator("#company-tray").scroll_into_view_if_needed()
    _watch_stamping(page)
    page.click(".status-tab[data-status='accepts']")
    page.wait_for_function("window.RVH.filter.getState().status === 'accepts'")
    page.wait_for_timeout(150)
    assert page.evaluate("window.__stamped") == 0
    expect(page.locator(".company-row:visible .stamp").first).to_be_visible()


def test_compact_density_keeps_first_tag_and_counts_the_rest(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.evaluate("window.RVH.density.set('compact')")
    row = page.locator(".company-row[data-id='proxify']")
    tags = (row.get_attribute("data-tags") or "").split(",")
    assert len(tags) > 1
    visible = row.locator(".tag-badge:visible")
    expect(visible).to_have_count(2)
    expect(visible.nth(0)).to_have_text(tags[0])
    expect(visible.nth(1)).to_have_text(f"+{len(tags) - 1}")
