"""E2E tests for the navbar settings menu: light/dark theme and table
density controls, including persistence across reloads."""

from __future__ import annotations

from playwright.sync_api import Page, expect


def _open_settings(page: Page) -> None:
    page.click('[data-testid="settings-toggle"]')
    expect(page.locator('[data-testid="settings-menu"]')).to_be_visible()


def test_settings_menu_opens_and_closes(page: Page, base_url: str) -> None:
    page.goto(base_url)
    menu = page.locator('[data-testid="settings-menu"]')
    expect(menu).to_be_hidden()
    page.click('[data-testid="settings-toggle"]')
    expect(menu).to_be_visible()
    # Clicking outside the menu closes it.
    page.click(".hero-title")
    expect(menu).to_be_hidden()


def test_page_starts_in_light_theme(page: Page, base_url: str) -> None:
    page.goto(base_url)
    expect(page.locator("html")).to_have_attribute("data-theme", "light")


def test_theme_switches_to_dark(page: Page, base_url: str) -> None:
    page.goto(base_url)
    _open_settings(page)
    page.click('[data-testid="theme-dark"]')
    page.wait_for_function("window.RVH.theme.get() === 'dark'")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")


def test_theme_switches_back_to_light(page: Page, base_url: str) -> None:
    page.goto(base_url)
    _open_settings(page)
    page.click('[data-testid="theme-dark"]')
    page.wait_for_function("window.RVH.theme.get() === 'dark'")
    page.click('[data-testid="theme-light"]')
    page.wait_for_function("window.RVH.theme.get() === 'light'")
    expect(page.locator("html")).to_have_attribute("data-theme", "light")


def test_theme_persists_across_reload(page: Page, base_url: str) -> None:
    page.goto(base_url)
    _open_settings(page)
    page.click('[data-testid="theme-dark"]')
    page.wait_for_function("window.RVH.theme.get() === 'dark'")
    page.reload()
    # The pre-paint hook in base.html applies the attribute before any module runs.
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")


def test_theme_changed_event_fires(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.evaluate(
        "window.__themeEvents = [];"
        "document.addEventListener('rvh:theme:changed', function (e) {"
        "  window.__themeEvents.push(e.detail);"
        "});"
    )
    _open_settings(page)
    page.click('[data-testid="theme-dark"]')
    page.wait_for_function("window.__themeEvents.length > 0")
    last = page.evaluate("window.__themeEvents.at(-1)")
    assert last["theme"] == "dark"


def test_compact_density_sets_attribute(page: Page, base_url: str) -> None:
    page.goto(base_url)
    _open_settings(page)
    page.click('[data-testid="density-compact"]')
    page.wait_for_function("window.RVH.density.get() === 'compact'")
    expect(page.locator("html")).to_have_attribute("data-density", "compact")


def test_density_persists_across_reload(page: Page, base_url: str) -> None:
    page.goto(base_url)
    _open_settings(page)
    page.click('[data-testid="density-compact"]')
    page.wait_for_function("window.RVH.density.get() === 'compact'")
    page.reload()
    expect(page.locator("html")).to_have_attribute("data-density", "compact")


def test_density_toggles_back_to_comfortable(page: Page, base_url: str) -> None:
    page.goto(base_url)
    _open_settings(page)
    page.click('[data-testid="density-compact"]')
    page.wait_for_function("window.RVH.density.get() === 'compact'")
    page.click('[data-testid="density-comfortable"]')
    page.wait_for_function("window.RVH.density.get() === 'comfortable'")
    expect(page.locator("html")).to_have_attribute("data-density", "comfortable")
