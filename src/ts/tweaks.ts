// tweaks.ts — Floating panel: accent color, dark mode, density.
//
// Patterns:
//   - Observable Store: tiny get/set/subscribe primitive. Three independent
//     effects (persist, applyToDOM, syncUI) subscribe and stay decoupled.
//   - Memento-lite: load/save to localStorage.
//   - Module/Namespace: exposes window.RVH.tweaks and emits
//     `rvh:tweaks:changed` on document for Playwright.

import type {
  AccentHex,
  Density,
  TweaksChangedDetail,
  TweaksState,
} from "./contracts";

declare const jQuery: JQueryStatic;

(function ($: JQueryStatic): void {
  "use strict";

  const STORAGE_KEY = "rvh-tweaks";
  const DEFAULTS: TweaksState = {
    accent: "#1d4ed8",
    darkMode: false,
    density: "Comfortable",
  };
  const ACCENTS: readonly AccentHex[] = [
    "#1d4ed8",
    "#6d28d9",
    "#0e7490",
    "#065f46",
  ];
  const ACCENT_LIGHTS: Record<AccentHex, string> = {
    "#1d4ed8": "#dbeafe",
    "#6d28d9": "#ede9fe",
    "#0e7490": "#cffafe",
    "#065f46": "#d1fae5",
  };
  const ACCENT_DARKS: Record<AccentHex, string> = {
    "#1d4ed8": "#3b82f6",
    "#6d28d9": "#8b5cf6",
    "#0e7490": "#06b6d4",
    "#065f46": "#10b981",
  };
  const DENSITIES: ReadonlyArray<{ value: Density; label: string }> = [
    { value: "Comfortable", label: "Cómoda" },
    { value: "Compact",     label: "Compacta" },
  ];

  function isAccent(value: string): value is AccentHex {
    return (ACCENTS as readonly string[]).indexOf(value) >= 0;
  }
  function isDensity(value: string): value is Density {
    return value === "Comfortable" || value === "Compact";
  }

  // ── Observable store ─────────────────────────────────────────────────
  type Subscriber = (state: TweaksState, patch: Partial<TweaksState> | null) => void;

  interface Store {
    get(): TweaksState;
    set(patch: Partial<TweaksState>): void;
    subscribe(fn: Subscriber): void;
  }

  function createStore(initial: TweaksState): Store {
    let state: TweaksState = initial;
    const subs: Subscriber[] = [];
    return {
      get: () => ({ ...state }),
      set: (patch) => {
        state = { ...state, ...patch };
        for (const fn of subs) fn(state, patch);
      },
      subscribe: (fn) => {
        subs.push(fn);
        fn(state, null);
      },
    };
  }

  // ── Persistence ──────────────────────────────────────────────────────
  function loadInitial(): TweaksState {
    try {
      const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}") as Partial<TweaksState>;
      const accent = raw.accent && isAccent(raw.accent) ? raw.accent : DEFAULTS.accent;
      const density = raw.density && isDensity(raw.density) ? raw.density : DEFAULTS.density;
      const darkMode = typeof raw.darkMode === "boolean" ? raw.darkMode : DEFAULTS.darkMode;
      return { accent, darkMode, density };
    } catch {
      return { ...DEFAULTS };
    }
  }
  function persist(state: TweaksState): void {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch { /* noop */ }
  }

  // ── Pure derivation: state → DOM attributes ──────────────────────────
  function applyToDOM(state: TweaksState): void {
    const root = document.documentElement;
    root.setAttribute("data-theme",   state.darkMode ? "dark" : "light");
    root.setAttribute("data-density", state.density);
    const accent = state.darkMode ? ACCENT_DARKS[state.accent] : state.accent;
    const accentLight = state.darkMode
      ? "rgba(59,130,246,0.12)"
      : ACCENT_LIGHTS[state.accent];
    root.style.setProperty("--accent",       accent);
    root.style.setProperty("--accent-light", accentLight);
  }

  // ── UI construction ──────────────────────────────────────────────────
  function buildUI(): { $fab: JQuery; $panel: JQuery } {
    const $fab = $(
      '<button type="button" class="tweaks-fab" data-testid="tweaks-fab" aria-label="Abrir panel de ajustes">' +
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
          '<circle cx="12" cy="12" r="3"/>' +
          '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>' +
        '</svg>' +
      '</button>',
    );

    const accentChips = ACCENTS.map((hex) =>
      `<button type="button" class="twk-chip" role="radio"` +
      ` data-accent="${hex}"` +
      ` data-testid="tweaks-accent-${hex.replace("#", "")}"` +
      ` aria-label="${hex}"` +
      ` style="background:${hex}"></button>`
    ).join("");

    const densitySeg = DENSITIES.map(
      (d) =>
        `<button type="button" role="radio"` +
        ` data-density="${d.value}"` +
        ` data-testid="tweaks-density-${d.value}">${d.label}</button>`
    ).join("");

    const $panel = $(
      '<div class="twk-panel" role="dialog" aria-label="Ajustes de visualización"' +
           ' data-testid="tweaks-panel" hidden>' +
        '<div class="twk-hd">' +
          '<b>Ajustes</b>' +
          '<button type="button" class="twk-x" data-testid="tweaks-close" aria-label="Cerrar">✕</button>' +
        '</div>' +
        '<div class="twk-body">' +
          '<div class="twk-sect">Color de acento</div>' +
          '<div class="twk-row">' +
            '<div class="twk-lbl">Color</div>' +
            '<div class="twk-chips" role="radiogroup" aria-label="Color de acento">' + accentChips + '</div>' +
          '</div>' +
          '<div class="twk-sect">Apariencia</div>' +
          '<div class="twk-row twk-row-h">' +
            '<div class="twk-lbl">Modo oscuro</div>' +
            '<button type="button" class="twk-toggle" data-tweak="darkMode"' +
              ' data-testid="tweaks-darkmode" role="switch" aria-label="Modo oscuro"><i></i></button>' +
          '</div>' +
          '<div class="twk-row">' +
            '<div class="twk-lbl">Densidad</div>' +
            '<div class="twk-seg" role="radiogroup" aria-label="Densidad">' + densitySeg + '</div>' +
          '</div>' +
        '</div>' +
      '</div>',
    );
    $panel.css("display", "none");

    $("body").append($panel).append($fab);
    return { $fab, $panel };
  }

  // ── Third subscriber: keep panel UI in sync with state ───────────────
  function makeSyncUI($panel: JQuery): (state: TweaksState) => void {
    const checkSvg =
      '<svg viewBox="0 0 14 14" aria-hidden="true">' +
        '<path d="M3 7.2 5.8 10 11 4.2" fill="none" stroke="#fff"' +
          ' stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>' +
      '</svg>';

    return function syncUI(state) {
      $panel.find("[data-accent]").each(function () {
        const $btn = $(this);
        const on = $btn.attr("data-accent") === state.accent;
        $btn
          .attr("data-on", on ? "1" : "0")
          .attr("aria-checked", on ? "true" : "false")
          .html(on ? checkSvg : "");
      });
      $panel.find('[data-tweak="darkMode"]')
        .attr("data-on", state.darkMode ? "1" : "0")
        .attr("aria-checked", state.darkMode ? "true" : "false");
      $panel.find("[data-density]").each(function () {
        const $btn = $(this);
        const on = $btn.attr("data-density") === state.density;
        $btn.attr("aria-checked", on ? "true" : "false");
      });
    };
  }

  // ── Wiring ───────────────────────────────────────────────────────────
  function bindControllers(store: Store, $fab: JQuery, $panel: JQuery): void {
    function togglePanel(open?: boolean): void {
      const willOpen = typeof open === "boolean" ? open : $panel.css("display") === "none";
      $panel.css("display", willOpen ? "flex" : "none")
            .attr("hidden", willOpen ? null : "");
      $(document).trigger("rvh:tweaks:toggled", [{ open: willOpen }]);
    }

    $fab.on("click", () => togglePanel());
    $panel.on("click", ".twk-x", () => togglePanel(false));
    $panel.on("click", "[data-accent]", function () {
      const raw = $(this).attr("data-accent") ?? "";
      if (isAccent(raw)) store.set({ accent: raw });
    });
    $panel.on("click", '[data-tweak="darkMode"]', () => {
      store.set({ darkMode: !store.get().darkMode });
    });
    $panel.on("click", "[data-density]", function () {
      const raw = $(this).attr("data-density") ?? "";
      if (isDensity(raw)) store.set({ density: raw });
    });

    $(document).on("mousedown.tweaks-outside", function (e) {
      if ($panel.css("display") === "none") return;
      const target = e.target as Node;
      const panelEl = $panel[0];
      const fabEl = $fab[0];
      if (!panelEl || !fabEl) return;
      if (panelEl === target || panelEl.contains(target)) return;
      if (fabEl   === target || fabEl.contains(target))   return;
      togglePanel(false);
    });
  }

  // ── Bootstrap ────────────────────────────────────────────────────────
  $(function () {
    const store = createStore(loadInitial());
    const ui = buildUI();

    store.subscribe((state, patch) => { if (patch) persist(state); });
    store.subscribe((state) => { applyToDOM(state); });
    store.subscribe(makeSyncUI(ui.$panel));
    store.subscribe((state, patch) => {
      if (patch) {
        const detail: TweaksChangedDetail = { state, patch };
        $(document).trigger("rvh:tweaks:changed", [detail]);
      }
    });

    bindControllers(store, ui.$fab, ui.$panel);

    window.RVH = window.RVH ?? {};
    window.RVH.tweaks = {
      get: store.get,
      set: store.set,
      reset: () => store.set({ ...DEFAULTS }),
    };
  });
})(jQuery);
