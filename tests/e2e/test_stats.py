"""E2E tests for the stats page."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect


def test_stats_page_renders_cards(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/stats.html")
    expect(page.locator(".stats-title")).to_have_text("Estadísticas")
    assert page.locator(".stat-card").count() == 5


def test_bar_charts_have_fills(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/stats.html")
    fills = page.locator(".bar-fill")
    assert fills.count() > 0
    style = fills.first.get_attribute("style") or ""
    assert "width" in style
    assert not re.search(r"width:\s*0%", style)


def test_nav_links_round_trip(page: Page, base_url: str) -> None:
    page.goto(base_url)
    page.click(".nav-link:has-text('Estadísticas')")
    expect(page).to_have_url(f"{base_url}/stats.html")
    page.click(".nav-link:has-text('Empresas')")
    expect(page).to_have_url(f"{base_url}/index.html")
