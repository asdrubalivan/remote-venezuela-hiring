// PROTOTIPO — comportamiento compartido de las 5 variantes + barra flotante.
//
// Contrato de markup (cada variante lo respeta con su propia estructura):
//   [data-rvh-row]            fila/entrada de empresa (data-status, data-search, data-name,
//                             data-last-checked, data-method, data-platform, data-tags, data-archived)
//   [data-rvh-group]          contenedor opcional de filas; se oculta si no le queda ninguna visible
//   [data-rvh-search]         input de búsqueda
//   [data-rvh-tab="all|accepts|rejects|unknown"]   pestañas de estado
//   [data-rvh-sort="name|status|last_checked|verification_method|hiring_platform"]  cabeceras ordenables
//   [data-rvh-filter="method|platform|tag"]        selects de filtro
//   [data-rvh-archived]       checkbox "Mostrar archivadas"
//   [data-rvh-filter-toggle] / [data-rvh-filter-panel]   botón "Filtros" y su panel (clase .is-open)
//   [data-rvh-filter-count]   contador de filtros activos dentro del botón
//   [data-rvh-clear]          botones que limpian filtros ([data-rvh-autohide] se oculta sin filtros)
//   [data-rvh-count]          contador de resultados ("N empresas")
//   [data-rvh-empty]          estado vacío
//   [data-rvh-settings-toggle] / [data-rvh-settings-menu]  ajustes de visualización
//   [data-rvh-theme="light|dark"], [data-rvh-density="comfortable|compact"]
//
// El escenario (#stage) refleja el estado en data-status, data-filtered y data-density,
// y emite el evento "rvh:applied" ({state, visible}) para los gestos propios de cada variante.
// Una variante puede registrar su JS con RVHProto.register(slug, (root) => cleanup?).
(function () {
  "use strict";

  var VARIANTS = window.RVH_PROTO_VARIANTS;
  var stage = document.getElementById("stage");
  var bar = document.getElementById("proto-bar");
  var params = new URLSearchParams(location.search);
  var current = 0;
  var cleanup = null;
  var state;

  function freshState() {
    return { status: "all", search: "", method: "all", platform: "all", tag: "all", archived: false, sort: "name", dir: "asc" };
  }

  function $$(sel) { return Array.prototype.slice.call(stage.querySelectorAll(sel)); }

  var SORTERS = {
    name: function (r) { return (r.dataset.name || "").toLowerCase(); },
    status: function (r) { return r.dataset.status || ""; },
    last_checked: function (r) { return r.dataset.lastChecked || ""; },
    verification_method: function (r) { return r.dataset.method || ""; },
    hiring_platform: function (r) { return r.dataset.platform || ""; },
  };

  function rowVisible(r) {
    if (!state.archived && r.dataset.archived === "1") return false;
    if (state.status !== "all" && r.dataset.status !== state.status) return false;
    if (state.method !== "all" && r.dataset.method !== state.method) return false;
    if (state.platform !== "all" && r.dataset.platform !== state.platform) return false;
    if (state.tag !== "all" && ("," + (r.dataset.tags || "") + ",").indexOf("," + state.tag + ",") < 0) return false;
    if (state.search && (r.dataset.search || "").indexOf(state.search) < 0) return false;
    return true;
  }

  function panelFilterCount() {
    return (state.method !== "all") + (state.platform !== "all") + (state.tag !== "all") + (state.archived ? 1 : 0);
  }

  function isFiltered() {
    return panelFilterCount() > 0 || state.status !== "all" || state.search !== "";
  }

  function apply() {
    var visible = 0;
    $$("[data-rvh-row]").forEach(function (r) {
      var show = rowVisible(r);
      r.hidden = !show;
      if (show) visible++;
    });
    $$("[data-rvh-group]").forEach(function (g) {
      g.hidden = !g.querySelector("[data-rvh-row]:not([hidden])");
    });
    $$("[data-rvh-count]").forEach(function (el) {
      el.textContent = visible + " empresa" + (visible !== 1 ? "s" : "");
    });
    $$("[data-rvh-empty]").forEach(function (el) { el.hidden = visible > 0; });
    $$("[data-rvh-tab]").forEach(function (t) {
      var on = t.getAttribute("data-rvh-tab") === state.status;
      t.classList.toggle("is-active", on);
      t.setAttribute("aria-selected", on ? "true" : "false");
    });
    var n = panelFilterCount();
    $$("[data-rvh-filter-count]").forEach(function (el) { el.textContent = String(n); el.hidden = n === 0; });
    $$("[data-rvh-clear][data-rvh-autohide]").forEach(function (el) { el.hidden = !isFiltered(); });
    $$("[data-rvh-sort]").forEach(function (h) {
      var on = h.getAttribute("data-rvh-sort") === state.sort;
      h.classList.toggle("is-active", on);
      h.setAttribute("aria-sort", on ? (state.dir === "asc" ? "ascending" : "descending") : "none");
      h.setAttribute("data-dir", on ? state.dir : "");
    });
    stage.dataset.status = state.status;
    stage.dataset.filtered = isFiltered() ? "true" : "false";
    renderBarState(visible);
    stage.dispatchEvent(new CustomEvent("rvh:applied", { detail: { state: Object.assign({}, state), visible: visible } }));
  }

  function sortRows() {
    var key = SORTERS[state.sort];
    var parents = [];
    $$("[data-rvh-row]").forEach(function (r) {
      if (parents.indexOf(r.parentElement) < 0) parents.push(r.parentElement);
    });
    parents.forEach(function (p) {
      var rows = Array.prototype.slice.call(p.children).filter(function (c) { return c.hasAttribute("data-rvh-row"); });
      rows.sort(function (a, b) {
        var x = key(a), y = key(b);
        var c = x < y ? -1 : x > y ? 1 : 0;
        return state.dir === "asc" ? c : -c;
      });
      rows.forEach(function (r) { p.appendChild(r); });
    });
  }

  function resetFilters() {
    var keepSort = { sort: state.sort, dir: state.dir };
    state = Object.assign(freshState(), keepSort);
    $$("[data-rvh-search]").forEach(function (i) { i.value = ""; });
    $$("[data-rvh-filter]").forEach(function (s) { s.value = "all"; });
    $$("[data-rvh-archived]").forEach(function (c) { c.checked = false; });
    apply();
  }

  function bind() {
    $$("[data-rvh-search]").forEach(function (input) {
      input.value = state.search;
      input.addEventListener("input", function () {
        state.search = input.value.trim().toLowerCase();
        apply();
      });
    });
    $$("[data-rvh-tab]").forEach(function (t) {
      t.addEventListener("click", function () {
        state.status = t.getAttribute("data-rvh-tab");
        apply();
      });
    });
    $$("[data-rvh-sort]").forEach(function (h) {
      h.addEventListener("click", function () {
        var key = h.getAttribute("data-rvh-sort");
        state.dir = state.sort === key && state.dir === "asc" ? "desc" : "asc";
        state.sort = key;
        sortRows();
        apply();
      });
    });
    $$("[data-rvh-filter]").forEach(function (s) {
      s.addEventListener("change", function () {
        state[s.getAttribute("data-rvh-filter")] = s.value;
        apply();
      });
    });
    $$("[data-rvh-archived]").forEach(function (c) {
      c.addEventListener("change", function () { state.archived = c.checked; apply(); });
    });
    $$("[data-rvh-clear]").forEach(function (b) { b.addEventListener("click", resetFilters); });
    $$("[data-rvh-filter-toggle]").forEach(function (b) {
      b.addEventListener("click", function () {
        var open = b.getAttribute("aria-expanded") !== "true";
        b.setAttribute("aria-expanded", open ? "true" : "false");
        $$("[data-rvh-filter-panel]").forEach(function (p) { p.classList.toggle("is-open", open); });
      });
    });
    $$("[data-rvh-settings-toggle]").forEach(function (b) {
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var open = b.getAttribute("aria-expanded") !== "true";
        b.setAttribute("aria-expanded", open ? "true" : "false");
        $$("[data-rvh-settings-menu]").forEach(function (m) { m.hidden = !open; });
      });
    });
    $$("[data-rvh-theme]").forEach(function (b) {
      b.addEventListener("click", function () {
        var theme = b.getAttribute("data-rvh-theme");
        document.documentElement.setAttribute("data-theme", theme);
        $$("[data-rvh-theme]").forEach(function (o) { o.setAttribute("aria-checked", o === b ? "true" : "false"); });
      });
    });
    $$("[data-rvh-density]").forEach(function (b) {
      b.addEventListener("click", function () {
        stage.dataset.density = b.getAttribute("data-rvh-density");
        $$("[data-rvh-density]").forEach(function (o) { o.setAttribute("aria-checked", o === b ? "true" : "false"); });
      });
    });
  }

  function renderBarState(visible) {
    var v = VARIANTS[current];
    document.getElementById("proto-bar-name").textContent = v.n + "/" + VARIANTS.length + " · " + v.name;
    var bits = ["estado: " + state.status];
    if (state.search) bits.push("búsqueda: “" + state.search + "”");
    if (panelFilterCount()) bits.push(panelFilterCount() + " filtro(s)");
    bits.push("orden: " + state.sort + " " + state.dir);
    bits.push(visible + " visibles");
    document.getElementById("proto-bar-state").textContent = bits.join(" · ");
    Array.prototype.forEach.call(bar.querySelectorAll("[data-proto-pick]"), function (b) {
      b.setAttribute("aria-current", Number(b.getAttribute("data-proto-pick")) === v.n ? "true" : "false");
    });
  }

  function mount(index, initial) {
    if (typeof cleanup === "function") cleanup();
    cleanup = null;
    current = (index + VARIANTS.length) % VARIANTS.length;
    var v = VARIANTS[current];
    var tpl = document.getElementById("tpl-" + v.n);
    stage.innerHTML = "";
    stage.appendChild(tpl.content.cloneNode(true));
    document.documentElement.setAttribute("data-proto", v.slug);
    document.documentElement.setAttribute("data-theme", "light");
    stage.dataset.density = "comfortable";
    state = Object.assign(freshState(), initial || {});
    bind();
    if (state.sort !== "name" || state.dir !== "asc") sortRows();
    apply();
    var hook = window.RVHProto.hooks[v.slug];
    if (hook) cleanup = hook(stage) || null;
    var url = new URL(location.href);
    url.searchParams.set("v", String(v.n));
    history.replaceState(null, "", url);
    window.scrollTo(0, 0);
  }

  bar.addEventListener("click", function (e) {
    var step = e.target.closest("[data-proto-step]");
    var pick = e.target.closest("[data-proto-pick]");
    if (step) mount(current + Number(step.getAttribute("data-proto-step")));
    if (pick) mount(Number(pick.getAttribute("data-proto-pick")) - 1);
  });

  document.addEventListener("keydown", function (e) {
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "select" || tag === "textarea" || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "ArrowRight") mount(current + 1);
    if (e.key === "ArrowLeft") mount(current - 1);
    if (/^[1-9]$/.test(e.key) && Number(e.key) <= VARIANTS.length) mount(Number(e.key) - 1);
  });

  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-rvh-settings-menu], [data-rvh-settings-toggle]")) return;
    $$("[data-rvh-settings-menu]").forEach(function (m) { m.hidden = true; });
    $$("[data-rvh-settings-toggle]").forEach(function (b) { b.setAttribute("aria-expanded", "false"); });
  });

  if (params.get("bar") === "0") bar.hidden = true;
  var initial = {};
  if (params.get("status")) initial.status = params.get("status");
  if (params.get("q")) initial.search = params.get("q").toLowerCase();
  mount(Math.max(0, (Number(params.get("v")) || 1) - 1), initial);

  window.RVHProto.mount = function (n, init) { mount(n - 1, init); };
  window.RVHProto.state = function () { return Object.assign({}, state); };
})();
