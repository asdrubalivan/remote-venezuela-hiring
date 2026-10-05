// PROTOTIPO — v5 Guía amarilla: el gesto firma.
//  · Índice A–Z del canto: salta a cada letra, atenúa las letras sin empresas
//    visibles y marca la letra del grupo que se está leyendo.
//  · Palabras guía: la cabecera muestra la primera y la última empresa visible
//    en la "página" (lo que queda bajo la cabecera pegajosa).
RVHProto.register("guia", function (root) {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var mobile = window.matchMedia("(max-width: 760px)");
  var slice = Array.prototype.slice;

  var table = root.querySelector(".dir");
  var thead = table ? table.querySelector("thead") : null;
  var rh = root.querySelector("[data-guia-rh]");
  var az = root.querySelector(".az");
  var list = root.querySelector(".az-list");
  var firstEl = root.querySelector("[data-guia-first]");
  var lastEl = root.querySelector("[data-guia-last]");
  var groups = slice.call(root.querySelectorAll("[data-guia-group]"));

  var tabs = {};
  slice.call(root.querySelectorAll("[data-guia-letter]")).forEach(function (a) {
    tabs[a.getAttribute("data-guia-letter")] = a;
  });
  var groupOf = {};
  groups.forEach(function (g) { groupOf[g.getAttribute("data-guia-group")] = g; });

  var inView = new Set();   // filas visibles bajo la cabecera pegajosa
  var crossing = new Set(); // grupo que cruza la línea de lectura
  var active = null;
  var rowIO = null;
  var groupIO = null;
  var raf = 0;
  var resizeTimer = 0;
  var hitTimer = 0;

  function offset() {
    var h = rh ? rh.offsetHeight : 0;
    if (mobile.matches) return h + (az ? az.offsetHeight : 0);
    return h + (thead ? thead.offsetHeight : 0);
  }

  function visibleRows() {
    return slice.call(root.querySelectorAll("[data-rvh-row]:not([hidden])"));
  }

  function setWord(el, text) {
    if (el && el.textContent !== text) el.textContent = text;
  }

  function revealTab(tab) {
    if (!mobile.matches || !list || list.scrollWidth <= list.clientWidth) return;
    var lr = list.getBoundingClientRect();
    var tr = tab.getBoundingClientRect();
    var left = list.scrollLeft + tr.left - lr.left - (list.clientWidth - tr.width) / 2;
    list.scrollTo({ left: Math.max(0, left), behavior: reduce.matches ? "auto" : "smooth" });
  }

  function setActive(letter) {
    if (letter === active) return;
    var prev = active && tabs[active];
    if (prev) {
      prev.classList.remove("is-active");
      prev.removeAttribute("aria-current");
    }
    active = letter;
    var tab = letter && tabs[letter];
    if (tab) {
      tab.classList.add("is-active");
      tab.setAttribute("aria-current", "location");
      revealTab(tab);
    }
  }

  function update() {
    raf = 0;
    var rows = visibleRows();
    var seen = rows.filter(function (r) { return inView.has(r); });
    var pool = seen.length ? seen : rows;
    setWord(firstEl, pool.length ? pool[0].getAttribute("data-name") : "");
    setWord(lastEl, pool.length ? pool[pool.length - 1].getAttribute("data-name") : "");

    var next = null;
    for (var i = 0; i < groups.length; i++) {
      if (!groups[i].hidden && crossing.has(groups[i])) { next = groups[i]; break; }
    }
    if (!next && table && rows.length) {
      var box = table.getBoundingClientRect();
      if (box.bottom < offset()) {
        var shown = groups.filter(function (g) { return !g.hidden; });
        next = shown[shown.length - 1] || null;
      }
    }
    setActive(next ? next.getAttribute("data-guia-group") : null);
  }

  function schedule() {
    if (!raf) raf = window.requestAnimationFrame(update);
  }

  function observe() {
    if (rowIO) rowIO.disconnect();
    if (groupIO) groupIO.disconnect();
    inView.clear();
    crossing.clear();
    var off = offset();
    rowIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) inView.add(e.target); else inView.delete(e.target);
      });
      schedule();
    }, { rootMargin: "-" + (off + 8) + "px 0px 0px 0px" });
    slice.call(root.querySelectorAll("[data-rvh-row]")).forEach(function (r) { rowIO.observe(r); });

    // Una franja de 2px justo bajo la cabecera: el grupo que la cruza es la letra activa.
    var bottom = Math.max(0, window.innerHeight - off - 12);
    groupIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) crossing.add(e.target); else crossing.delete(e.target);
      });
      schedule();
    }, { rootMargin: "-" + (off + 10) + "px 0px -" + bottom + "px 0px" });
    groups.forEach(function (g) { groupIO.observe(g); });
  }

  // Letras sin empresas visibles: atenuadas y fuera del orden de tabulación.
  function syncIndex() {
    Object.keys(tabs).forEach(function (letter) {
      var a = tabs[letter];
      var g = groupOf[letter];
      if (g && !g.hidden) {
        a.setAttribute("href", "#guia-" + letter);
        a.removeAttribute("aria-disabled");
      } else {
        a.removeAttribute("href");
        a.setAttribute("aria-disabled", "true");
      }
    });
  }

  function flash(th) {
    if (reduce.matches) return;
    th.classList.remove("is-hit");
    void th.offsetWidth;
    th.classList.add("is-hit");
    window.clearTimeout(hitTimer);
    hitTimer = window.setTimeout(function () { th.classList.remove("is-hit"); }, 1300);
  }

  function onClick(e) {
    var a = e.target.closest ? e.target.closest("[data-guia-letter]") : null;
    if (!a || !root.contains(a)) return;
    e.preventDefault();
    if (a.getAttribute("aria-disabled") === "true") return;
    var letter = a.getAttribute("data-guia-letter");
    var g = groupOf[letter];
    var th = g && g.querySelector(".grp-letter");
    if (!th) return;
    th.scrollIntoView({ behavior: reduce.matches ? "auto" : "smooth", block: "start" });
    th.focus({ preventScroll: true });
    setActive(letter);
    // El destello llega cuando termina el salto.
    var done = false;
    function land() {
      if (done) return;
      done = true;
      window.removeEventListener("scrollend", land);
      flash(th);
    }
    if ("onscrollend" in window) window.addEventListener("scrollend", land, { once: true });
    window.setTimeout(land, reduce.matches ? 0 : 700);
  }

  function onApplied() {
    syncIndex();
    schedule();
  }

  function onResize() {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(function () { observe(); schedule(); }, 150);
  }

  root.addEventListener("click", onClick);
  root.addEventListener("rvh:applied", onApplied);
  window.addEventListener("resize", onResize);

  syncIndex();
  observe();
  schedule();

  return function cleanup() {
    root.removeEventListener("click", onClick);
    root.removeEventListener("rvh:applied", onApplied);
    window.removeEventListener("resize", onResize);
    if (rowIO) rowIO.disconnect();
    if (groupIO) groupIO.disconnect();
    if (raf) window.cancelAnimationFrame(raf);
    window.clearTimeout(resizeTimer);
    window.clearTimeout(hitTimer);
  };
});
