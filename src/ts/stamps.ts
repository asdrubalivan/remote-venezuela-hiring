// stamps.ts — The Boleto signature gesture.
//
// When a status tab, filter or search changes the visible coupons, the
// stamps of the first coupons in the viewport are stamped once, staggered.
// Every other stamp is already inked: the stamp is visible by default, sorting
// never re-stamps, and with prefers-reduced-motion nothing animates at all.
//
// Listens to filter.ts's `rvh:filter:applied` event; no other coupling.

import type { FilterAppliedDetail, FilterState } from "./contracts";

(function (): void {
  "use strict";

  const table = document.getElementById("company-table");
  if (!table) return;

  const MAX_STAMPS = 8;
  const SEARCH_PAUSE_MS = 220;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");

  let timer: ReturnType<typeof setTimeout> | null = null;
  let lastSearch: string | null = null;
  let lastRest: string | null = null;

  function restKey(s: FilterState): string {
    return [s.status, s.method, s.platform, s.tag, s.archived ? 1 : 0].join("|");
  }

  function stamp(): void {
    if (reduce.matches) return;
    for (const row of Array.from(table!.querySelectorAll(".is-stamping"))) {
      row.classList.remove("is-stamping");
    }
    const height = window.innerHeight;
    const rows = table!.querySelectorAll<HTMLElement>(".company-row");
    let n = 0;
    for (const row of Array.from(rows)) {
      if (n >= MAX_STAMPS) break;
      if (row.style.display === "none") continue;
      const r = row.getBoundingClientRect();
      if (r.bottom <= 0) continue;
      if (r.top >= height) break;
      row.style.setProperty("--i", String(n));
      void row.offsetWidth; // restart the animation if it was mid-stamp
      row.classList.add("is-stamping");
      n += 1;
    }
  }

  // filter.js runs first and has already rendered once: take its state as the
  // baseline so the first real change is recognised as one.
  const initial = window.RVH?.filter?.getState();
  if (initial) {
    lastRest = restKey(initial);
    lastSearch = initial.search;
  }

  document.addEventListener("rvh:filter:applied", (e) => {
    const { state } = (e as CustomEvent<FilterAppliedDetail>).detail;
    const rest = restKey(state);
    if (lastRest === null) {
      lastRest = rest;
      lastSearch = state.search;
      return;
    }
    const searchChanged = state.search !== lastSearch;
    if (rest === lastRest && !searchChanged) return; // sorting does not re-stamp
    const searchOnly = rest === lastRest;
    lastRest = rest;
    lastSearch = state.search;
    if (timer) clearTimeout(timer);
    // While typing, wait for a short pause instead of stamping on every key.
    timer = setTimeout(stamp, searchOnly ? SEARCH_PAUSE_MS : 0);
  });

  table.addEventListener("animationend", (e) => {
    const row = (e.target as HTMLElement).closest<HTMLElement>(".company-row");
    if (!row) return;
    const last = row.querySelector(".stale-marker") ? "estampar-mini" : "estampar";
    if (e.animationName === last) row.classList.remove("is-stamping");
  });

  // Arrival: the booklet comes in stamping the coupons already on screen.
  window.requestAnimationFrame(stamp);
})();
