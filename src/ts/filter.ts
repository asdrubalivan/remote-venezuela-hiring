// filter.ts — Index page filtering, sorting and status tabs.
//
// Patterns:
//   - Reducer: every interaction becomes a discriminated `FilterAction`;
//     `reduce(state, action)` is pure and exhaustively typed.
//   - Strategy maps: FILTERS and SORTERS are objects keyed by column/filter
//     name, so adding a new column is one entry, not an if/else branch.
//   - Module/Namespace: exposes window.RVH.filter for tests + custom event
//     `rvh:filter:applied` for async-friendly Playwright waits.
//
// jQuery is loaded from CDN as a global; declared here as `$` only for typing.

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

declare const jQuery: JQueryStatic;

(function ($: JQueryStatic): void {
  "use strict";

  const $table = $("#company-table");
  if ($table.length === 0) return;

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
  const $tbody          = $table.find("tbody");
  const tbodyEl         = $tbody[0] as HTMLElement;
  const rows: HTMLElement[] = $tbody.find(".company-row").toArray();
  const $statusTabs     = $(".status-tab");
  const $sortHeaders    = $(".sort-th");
  const $clearBtn       = $("#clear-filters");
  const $emptyState     = $("#empty-state");
  const $resultsCounter = $("#results-counter");

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
    $statusTabs.each(function () {
      const $tab = $(this);
      const key = String($tab.data("status")) as Status;
      const isActive = state.status === key;
      $tab
        .toggleClass("is-active", isActive)
        .attr("aria-selected", isActive ? "true" : "false");
      const count = counts[key] ?? 0;
      $tab.find(".status-tab-count").text(String(count));
    });

    const totalForStatus =
      state.status === "all" ? counts.all : (counts[state.status] ?? 0);
    if (visible.length !== totalForStatus) {
      $resultsCounter.text(visible.length + " de " + counts.all + " empresas");
    } else {
      $resultsCounter.text(
        visible.length + " empresa" + (visible.length !== 1 ? "s" : ""),
      );
    }

    $clearBtn.toggleClass("is-hidden", !hasActiveFilters(state));

    if (visible.length === 0) {
      $emptyState.prop("hidden", false);
      $table.css("display", "none");
    } else {
      $emptyState.prop("hidden", true);
      $table.css("display", "");
    }

    $sortHeaders.each(function () {
      const $th = $(this);
      const arrow = $th.find(".sort-arrow");
      if ($th.data("sort") === state.sortBy) {
        $th.addClass("is-active");
        arrow.text(state.sortDir === "asc" ? "▲" : "▼");
        $th.attr(
          "aria-sort",
          state.sortDir === "asc" ? "ascending" : "descending",
        );
      } else {
        $th.removeClass("is-active");
        arrow.text("⇅");
        $th.attr("aria-sort", "none");
      }
    });

    const detail: FilterAppliedDetail = { state, visible: visible.length };
    $(document).trigger("rvh:filter:applied", [detail]);
  }

  function dispatch(action: FilterAction): void {
    state = reduce(state, action);
    render();
  }

  // ── Controllers (jQuery delegation, debounced search) ────────────────
  let searchTimer: ReturnType<typeof setTimeout> | null = null;
  $("#company-search").on("input", function () {
    const v = String($(this).val() ?? "").trim().toLowerCase();
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => dispatch({ type: "SEARCH", value: v }), 120);
  });

  $("#filter-method").on("change", function () {
    dispatch({ type: "FILTER", patch: { method: (this as HTMLSelectElement).value } });
  });
  $("#filter-platform").on("change", function () {
    dispatch({ type: "FILTER", patch: { platform: (this as HTMLSelectElement).value } });
  });
  $("#filter-tag").on("change", function () {
    dispatch({ type: "FILTER", patch: { tag: (this as HTMLSelectElement).value } });
  });
  $("#filter-archived").on("change", function () {
    dispatch({ type: "ARCHIVED", value: (this as HTMLInputElement).checked });
  });

  $statusTabs.on("click", function () {
    const raw = String($(this).data("status"));
    if (isStatus(raw)) dispatch({ type: "STATUS", value: raw });
  });
  $sortHeaders.on("click", function () {
    const raw = String($(this).data("sort"));
    if (isSortKey(raw)) dispatch({ type: "SORT", key: raw });
  });
  $("#clear-filters, #empty-clear").on("click", function () {
    $("#company-search").val("");
    $("#filter-method, #filter-platform, #filter-tag").val("all");
    dispatch({ type: "CLEAR" });
  });

  // ── Public API for Playwright ────────────────────────────────────────
  window.RVH = window.RVH ?? {};
  window.RVH.filter = {
    getState: () => ({ ...state }),
    dispatch,
    rowCount: () => rows.length,
  };

  render();
})(jQuery);
