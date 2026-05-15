"""E2E tests for the Tweaks panel: dark mode, accent, density, persistence."""

from __future__ import annotations

from playwright.sync_api import Page, expect


def test_tweaks_panel_opens(page: Page, base_url: str) -> None:
    page.goto(base_url)
    panel = page.locator('[data-testid="tweaks-panel"]')
    expect(panel).to_be_hidden()
    page.click('[data-testid="tweaks-fab"]')
    expect(panel).to_be_visible()


def test_dark_mode_toggle(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click('[data-testid="tweaks-fab"]')
    page.click('[data-testid="tweaks-darkmode"]')
    page.wait_for_function("window.RVH.tweaks.get().darkMode === true")
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")


def test_dark_mode_persists_across_reload(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click('[data-testid="tweaks-fab"]')
    page.click('[data-testid="tweaks-darkmode"]')
    page.wait_for_function("window.RVH.tweaks.get().darkMode === true")
    page.reload()
    # The pre-paint hook in base.html applies the attribute before any JS module runs.
    expect(page.locator("html")).to_have_attribute("data-theme", "dark")


def test_accent_color_changes_css_variable(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click('[data-testid="tweaks-fab"]')
    page.click('[data-testid="tweaks-accent-6d28d9"]')  # purple
    page.wait_for_function("window.RVH.tweaks.get().accent === '#6d28d9'")
    accent = page.evaluate(
        "getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"
    )
    assert accent.startswith("#6d28d9") or accent == "#6d28d9"


def test_density_compact_sets_attribute(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click('[data-testid="tweaks-fab"]')
    page.click('[data-testid="tweaks-density-Compact"]')
    page.wait_for_function("window.RVH.tweaks.get().density === 'Compact'")
    expect(page.locator("html")).to_have_attribute("data-density", "Compact")


def test_tweaks_changed_event_fires(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.evaluate(
        "window.__tweaksEvents = [];"
        "jQuery(document).on('rvh:tweaks:changed', function (e, payload) {"
        "  window.__tweaksEvents.push(payload);"
        "});"
    )
    page.click('[data-testid="tweaks-fab"]')
    page.click('[data-testid="tweaks-darkmode"]')
    page.wait_for_function("window.__tweaksEvents.length > 0")
    last = page.evaluate("window.__tweaksEvents.at(-1)")
    assert last["state"]["darkMode"] is True
    assert last["patch"]["darkMode"] is True


def test_close_button_hides_panel(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click('[data-testid="tweaks-fab"]')
    expect(page.locator('[data-testid="tweaks-panel"]')).to_be_visible()
    page.click('[data-testid="tweaks-close"]')
    expect(page.locator('[data-testid="tweaks-panel"]')).to_be_hidden()
