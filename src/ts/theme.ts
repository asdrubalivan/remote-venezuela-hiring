// theme.ts — Display preferences: light/dark theme + table density.
//
// The pre-paint inline script in base.html has already applied the persisted
// (or OS-preferred) theme and density to <html> before this module runs, so
// here we only wire the controls, persist changes, and expose a small API on
// window.RVH for Playwright.
//
// Both controls live in the navbar settings menu (#settings-toggle opens
// #settings-menu), each a segmented radiogroup.

import type { Density, Theme, ThemeChangedDetail } from "./contracts";

(function (): void {
  "use strict";

  const THEME_KEY = "rvh-theme";
  const DENSITY_KEY = "rvh-density";
  const root = document.documentElement;

  function store(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch {
      /* localStorage unavailable — preference still applies for the session */
    }
  }

  // ── Theme ──────────────────────────────────────────────────────────────
  const themeBtns = Array.from(
    document.querySelectorAll<HTMLElement>(".settings-seg-btn[data-theme]"),
  );

  function currentTheme(): Theme {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function syncThemeUI(): void {
    const active = currentTheme();
    for (const btn of themeBtns) {
      btn.setAttribute("aria-checked", btn.dataset["theme"] === active ? "true" : "false");
    }
  }

  function setTheme(theme: Theme): void {
    root.setAttribute("data-theme", theme);
    store(THEME_KEY, theme);
    syncThemeUI();
    const detail: ThemeChangedDetail = { theme };
    document.dispatchEvent(new CustomEvent("rvh:theme:changed", { detail }));
  }

  function toggleTheme(): void {
    setTheme(currentTheme() === "dark" ? "light" : "dark");
  }

  for (const btn of themeBtns) {
    btn.addEventListener("click", () => {
      const value = btn.dataset["theme"];
      if (value === "light" || value === "dark") setTheme(value);
    });
  }
  syncThemeUI();

  // ── Density ────────────────────────────────────────────────────────────
  const densityBtns = Array.from(
    document.querySelectorAll<HTMLElement>(".settings-seg-btn[data-density]"),
  );

  function currentDensity(): Density {
    return root.getAttribute("data-density") === "compact" ? "compact" : "comfortable";
  }

  function syncDensityUI(): void {
    const active = currentDensity();
    for (const btn of densityBtns) {
      btn.setAttribute("aria-checked", btn.dataset["density"] === active ? "true" : "false");
    }
  }

  function setDensity(density: Density): void {
    root.setAttribute("data-density", density);
    store(DENSITY_KEY, density);
    syncDensityUI();
  }

  for (const btn of densityBtns) {
    btn.addEventListener("click", () => {
      const value = btn.dataset["density"];
      if (value === "comfortable" || value === "compact") setDensity(value);
    });
  }
  syncDensityUI();

  // ── Settings menu (open / close) ──────────────────────────────────────
  const menuBtn = document.getElementById("settings-toggle");
  const menu = document.getElementById("settings-menu");

  function setMenuOpen(open: boolean): void {
    if (!menu || !menuBtn) return;
    menu.hidden = !open;
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  menuBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    setMenuOpen(menu?.hidden ?? false);
  });

  document.addEventListener("click", (e) => {
    if (!menu || menu.hidden) return;
    const target = e.target as Node;
    if (menu.contains(target) || menuBtn?.contains(target)) return;
    setMenuOpen(false);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && menu && !menu.hidden) {
      setMenuOpen(false);
      menuBtn?.focus();
    }
  });

  // ── Public API for Playwright ─────────────────────────────────────────
  window.RVH = window.RVH ?? {};
  window.RVH.theme = { get: currentTheme, set: setTheme, toggle: toggleTheme };
  window.RVH.density = { get: currentDensity, set: setDensity };
})();
