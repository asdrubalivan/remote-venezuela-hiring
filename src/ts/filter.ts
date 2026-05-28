// filter.ts — Index page filtering, sorting, status tabs and active-filter
// chips. Vanilla TypeScript, no framework.
//
// Patterns:
//   - Reducer: every interaction becomes a discriminated `FilterAction`;
//     `reduce(state, action)` is pure and exhaustively typed.
//   - Strategy maps: FILTERS and SORTERS are objects keyed by column/filter
//     name, so adding a new column is one entry, not an if/else branch.
//   - Module/Namespace: exposes window.RVH.filter for tests + native custom
//     event `rvh:filter:applied` for async-friendly Playwright waits.

import {
  type FilterAction,
  type FilterAppliedDetail,
  type FilterState,
  type SortKey,
  type Status,
  assertNever,
  isSortKey,
  isStatus,
} from "./contracts";

(function (): void {
  "use strict";

  const table = document.getElementById("company-table");
  if (!table) return;

  // ── Strategy maps ────────────────────────────────────────────────────
  const FILTERS: Record<string, (row: HTMLElement, s: FilterState) => boolean> = {
    archived: (row, s) => s.archived || row.dataset["archived"] !== "1",
    status:   (row, s) => s.status === "all"   || row.dataset["status"] === s.status,
    method:   (row, s) => s.method === "all"   || row.dataset["method"] === s.method,
    platform: (row, s) => s.platform === "all" || row.dataset["platform"] === s.platform,
    tag:      (row, s) => {
      if (s.tag === "all") return true;
      const tags = "," + (row.dataset["tags"] ?? "") + ",";
      return tags.indexOf("," + s.tag + ",") >= 0;
    },
    search:   (row, s) =>
      !s.search || (row.dataset["search"] ?? "").indexOf(s.search) >= 0,
  };

  const SORTERS: Record<SortKey, (row: HTMLElement) => string> = {
    name:                (row) => (row.dataset["name"] ?? "").toLowerCase(),
    status:              (row) => row.dataset["status"] ?? "",
    last_checked:        (row) => row.dataset["lastChecked"] ?? "",
    verification_method: (row) => row.dataset["method"] ?? "",
    hiring_platform:     (row) => row.dataset["platform"] ?? "",
  };

  // ── DOM refs (captured once) ─────────────────────────────────────────
  const tbodyEl     = table.querySelector("tbody") as HTMLElement;
  const rows        = Array.from(tbodyEl.querySelectorAll<HTMLElement>(".company-row"));
  const statusTabs  = Array.from(document.querySelectorAll<HTMLElement>(".status-tab"));
  const sortHeaders = Array.from(document.querySelectorAll<HTMLElement>(".sort-th"));
  const clearBtn        = document.getElementById("clear-filters");
  const emptyState      = document.getElementById("empty-state");
  const resultsCounter  = document.getElementById("results-counter");
  const chipsEl         = document.getElementById("filter-chips");
  const searchInput     = document.getElementById("company-search") as HTMLInputElement | null;
  const methodSel       = document.getElementById("filter-method") as HTMLSelectElement | null;
  const platformSel     = document.getElementById("filter-platform") as HTMLSelectElement | null;
  const tagSel          = document.getElementById("filter-tag") as HTMLSelectElement | null;
  const archivedCheck   = document.getElementById("filter-archived") as HTMLInputElement | null;
  const filterToggle    = document.getElementById("filter-toggle");
  const filterPanel     = document.getElementById("filter-panel");
  const filterToggleCnt = document.getElementById("filter-toggle-count");

  // Status-tab labels, read once (text node minus dot and count badge).
  const statusLabels: Record<string, string> = {};
  for (const tab of statusTabs) {
    const key = String(tab.dataset["status"]);
    const clone = tab.cloneNode(true) as HTMLElement;
    clone.querySelector(".status-tab-count")?.remove();
    clone.querySelector(".status-dot")?.remove();
    statusLabels[key] = (clone.textContent ?? "").trim();
  }

  function optionLabel(sel: HTMLSelectElement | null, value: string): string {
    if (!sel) return value;
    for (const opt of Array.from(sel.options)) {
      if (opt.value === value) return opt.text;
    }
    return value;
  }

  // ── State ────────────────────────────────────────────────────────────
  const initialState: FilterState = {
    search: "",
    status: "all",
    method: "all",
    platform: "all",
    tag: "all",
    archived: false,
    sortBy: "name",
    sortDir: "asc",
  };
  let state: FilterState = { ...initialState };

  // ── Reducer (exhaustive) ─────────────────────────────────────────────
  function reduce(s: FilterState, a: FilterAction): FilterState {
    switch (a.type) {
      case "SEARCH":   return { ...s, search: a.value };
      case "FILTER":   return { ...s, ...a.patch };
      case "STATUS":   return { ...s, status: a.value };
      case "ARCHIVED": return { ...s, archived: a.value };
      case "SORT":
        if (s.sortBy === a.key) {
          return { ...s, sortDir: s.sortDir === "asc" ? "desc" : "asc" };
        }
        return { ...s, sortBy: a.key, sortDir: "asc" };
      case "CLEAR":
        return {
          ...s,
          search: "",
          status: "all",
          method: "all",
          platform: "all",
          tag: "all",
        };
      default:
        return assertNever(a);
    }
  }

  // ── Pure helpers ─────────────────────────────────────────────────────
  function rowMatches(row: HTMLElement, s: FilterState): boolean {
    for (const key in FILTERS) {
      const predicate = FILTERS[key];
      if (predicate && !predicate(row, s)) return false;
    }
    return true;
  }

  type StatusCounts = Record<Status, number>;

  function countByStatus(s: FilterState): StatusCounts {
    const counts: StatusCounts = { all: 0, accepts: 0, rejects: 0, unknown: 0 };
    for (const row of rows) {
      if (!s.archived && row.dataset["archived"] === "1") continue;
      counts.all += 1;
      const rowStatus = row.dataset["status"];
      if (rowStatus === "accepts" || rowStatus === "rejects" || rowStatus === "unknown") {
        counts[rowStatus] += 1;
      }
    }
    return counts;
  }

  function hasActiveFilters(s: FilterState): boolean {
    return (
      s.status !== "all" ||
      s.method !== "all" ||
      s.platform !== "all" ||
      s.tag !== "all" ||
      s.search !== ""
    );
  }

  // ── Active-filter chips ──────────────────────────────────────────────
  type ChipKind = "search" | "status" | "method" | "platform" | "tag";

  function renderChips(s: FilterState): void {
    if (!chipsEl) return;
    const chips: Array<{ kind: ChipKind; label: string }> = [];
    if (s.search) chips.push({ kind: "search", label: `“${s.search}”` });
    if (s.status !== "all") {
      chips.push({ kind: "status", label: statusLabels[s.status] ?? s.status });
    }
    if (s.method !== "all") {
      chips.push({ kind: "method", label: optionLabel(methodSel, s.method) });
    }
    if (s.platform !== "all") {
      chips.push({ kind: "platform", label: optionLabel(platformSel, s.platform) });
    }
    if (s.tag !== "all") chips.push({ kind: "tag", label: s.tag });

    chipsEl.textContent = "";
    for (const chip of chips) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "filter-chip";
      btn.dataset["clear"] = chip.kind;
      btn.setAttribute("aria-label", `Quitar filtro: ${chip.label}`);
      const text = document.createElement("span");
      text.textContent = chip.label;
      const x = document.createElement("span");
      x.className = "filter-chip-x";
      x.setAttribute("aria-hidden", "true");
      x.textContent = "✕";
      btn.append(text, x);
      chipsEl.appendChild(btn);
    }
  }

  function updateFilterToggle(s: FilterState): void {
    if (!filterToggleCnt) return;
    let n = 0;
    if (s.method !== "all") n += 1;
    if (s.platform !== "all") n += 1;
    if (s.tag !== "all") n += 1;
    if (s.archived) n += 1;
    if (n > 0) {
      filterToggleCnt.textContent = String(n);
      filterToggleCnt.hidden = false;
    } else {
      filterToggleCnt.hidden = true;
    }
  }

  // ── Render (idempotent) ──────────────────────────────────────────────
  function render(): void {
    const visible: HTMLElement[] = [];
    for (const row of rows) {
      if (rowMatches(row, state)) {
        visible.push(row);
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    }

    const sorter = SORTERS[state.sortBy];
    const dir = state.sortDir === "asc" ? 1 : -1;
    visible.sort((a, b) => {
      const av = sorter(a);
      const bv = sorter(b);
      if (av < bv) return -1 * dir;
      if (av > bv) return  1 * dir;
      return 0;
    });

    const frag = document.createDocumentFragment();
    for (const row of visible) frag.appendChild(row);
    tbodyEl.appendChild(frag);

    const counts = countByStatus(state);
    for (const tab of statusTabs) {
      const key = String(tab.dataset["status"]) as Status;
      const isActive = state.status === key;
      tab.classList.toggle("is-active", isActive);
      tab.setAttribute("aria-selected", isActive ? "true" : "false");
      const countEl = tab.querySelector(".status-tab-count");
      if (countEl) countEl.textContent = String(counts[key] ?? 0);
    }

    if (resultsCounter) {
      const totalForStatus =
        state.status === "all" ? counts.all : (counts[state.status] ?? 0);
      if (visible.length !== totalForStatus) {
        resultsCounter.textContent = visible.length + " de " + counts.all + " empresas";
      } else {
        resultsCounter.textContent =
          visible.length + " empresa" + (visible.length !== 1 ? "s" : "");
      }
    }

    clearBtn?.classList.toggle("is-hidden", !hasActiveFilters(state));

    if (emptyState && (table as HTMLElement)) {
      if (visible.length === 0) {
        emptyState.hidden = false;
        (table as HTMLElement).style.display = "none";
      } else {
        emptyState.hidden = true;
        (table as HTMLElement).style.display = "";
      }
    }

    for (const th of sortHeaders) {
      const arrow = th.querySelector(".sort-arrow");
      if (th.dataset["sort"] === state.sortBy) {
        th.classList.add("is-active");
        if (arrow) arrow.textContent = state.sortDir === "asc" ? "▲" : "▼";
        th.setAttribute("aria-sort", state.sortDir === "asc" ? "ascending" : "descending");
      } else {
        th.classList.remove("is-active");
        if (arrow) arrow.textContent = "⇅";
        th.setAttribute("aria-sort", "none");
      }
    }

    renderChips(state);
    updateFilterToggle(state);

    const detail: FilterAppliedDetail = { state, visible: visible.length };
    document.dispatchEvent(new CustomEvent("rvh:filter:applied", { detail }));
  }

  function dispatch(action: FilterAction): void {
    state = reduce(state, action);
    render();
  }

  function resetControls(): void {
    if (searchInput) searchInput.value = "";
    if (methodSel) methodSel.value = "all";
    if (platformSel) platformSel.value = "all";
    if (tagSel) tagSel.value = "all";
  }

  // ── Controllers ──────────────────────────────────────────────────────
  let searchTimer: ReturnType<typeof setTimeout> | null = null;
  searchInput?.addEventListener("input", () => {
    const v = String(searchInput.value ?? "").trim().toLowerCase();
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => dispatch({ type: "SEARCH", value: v }), 120);
  });

  methodSel?.addEventListener("change", () => {
    dispatch({ type: "FILTER", patch: { method: methodSel.value } });
  });
  platformSel?.addEventListener("change", () => {
    dispatch({ type: "FILTER", patch: { platform: platformSel.value } });
  });
  tagSel?.addEventListener("change", () => {
    dispatch({ type: "FILTER", patch: { tag: tagSel.value } });
  });
  archivedCheck?.addEventListener("change", () => {
    dispatch({ type: "ARCHIVED", value: archivedCheck.checked });
  });

  for (const tab of statusTabs) {
    tab.addEventListener("click", () => {
      const raw = String(tab.dataset["status"]);
      if (isStatus(raw)) dispatch({ type: "STATUS", value: raw });
    });
  }
  for (const th of sortHeaders) {
    th.addEventListener("click", () => {
      const raw = String(th.dataset["sort"]);
      if (isSortKey(raw)) dispatch({ type: "SORT", key: raw });
    });
  }

  function clearAll(): void {
    resetControls();
    dispatch({ type: "CLEAR" });
  }
  clearBtn?.addEventListener("click", clearAll);
  document.getElementById("empty-clear")?.addEventListener("click", clearAll);

  // Per-chip removal (event delegation).
  chipsEl?.addEventListener("click", (e) => {
    const chip = (e.target as HTMLElement).closest<HTMLElement>(".filter-chip");
    if (!chip) return;
    switch (chip.dataset["clear"]) {
      case "search":
        if (searchInput) searchInput.value = "";
        dispatch({ type: "SEARCH", value: "" });
        break;
      case "status":
        dispatch({ type: "STATUS", value: "all" });
        break;
      case "method":
        if (methodSel) methodSel.value = "all";
        dispatch({ type: "FILTER", patch: { method: "all" } });
        break;
      case "platform":
        if (platformSel) platformSel.value = "all";
        dispatch({ type: "FILTER", patch: { platform: "all" } });
        break;
      case "tag":
        if (tagSel) tagSel.value = "all";
        dispatch({ type: "FILTER", patch: { tag: "all" } });
        break;
      default:
        break;
    }
  });

  // Mobile: collapsible filter panel.
  filterToggle?.addEventListener("click", () => {
    if (!filterPanel) return;
    const collapsed = filterPanel.classList.toggle("is-collapsed");
    filterToggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
  });

  // ── Public API for Playwright ────────────────────────────────────────
  window.RVH = window.RVH ?? {};
  window.RVH.filter = {
    getState: () => ({ ...state }),
    dispatch,
    rowCount: () => rows.length,
  };

  render();
})();
