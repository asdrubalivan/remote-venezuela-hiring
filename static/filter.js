// Client-side filter for the company table.
// Reads from data-search and data-status attributes set by the template.
(function () {
  "use strict";

  const searchInput = document.getElementById("company-search");
  const statusFilter = document.querySelector(".status-filter");
  const table = document.getElementById("company-table");
  const emptyState = document.getElementById("empty-state");

  if (!searchInput || !statusFilter || !table || !emptyState) {
    return;
  }

  const rows = Array.from(table.querySelectorAll("tbody tr.company-row"));

  function activeStatuses() {
    const boxes = statusFilter.querySelectorAll("input[type=checkbox]");
    const active = new Set();
    boxes.forEach((box) => {
      if (box.checked) {
        active.add(box.value);
      }
    });
    return active;
  }

  function applyFilter() {
    const query = searchInput.value.trim().toLowerCase();
    const statuses = activeStatuses();
    let visible = 0;

    rows.forEach((row) => {
      const search = row.dataset.search || "";
      const status = row.dataset.status || "";
      const matchesQuery = query.length === 0 || search.includes(query);
      const matchesStatus = statuses.has(status);
      const show = matchesQuery && matchesStatus;
      row.hidden = !show;
      if (show) visible += 1;
    });

    emptyState.hidden = visible !== 0;
  }

  searchInput.addEventListener("input", applyFilter);
  statusFilter.addEventListener("change", applyFilter);
})();
