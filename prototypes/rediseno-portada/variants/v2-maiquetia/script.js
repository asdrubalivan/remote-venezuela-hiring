// PROTOTIPO — v2 Piso de Maiquetía. Código descartable.
//
// Gesto firma (inducción cromática): el color del piso lo decide CSS a partir de
// #stage[data-status]; aquí solo se marca
//   - data-mq-dir: hacia dónde viaja la ola (izquierda→derecha si la pestaña nueva
//     está a la derecha de la anterior, y al revés),
//   - data-mq-empty: sin resultados el piso se apaga (solo quedan las líneas negras),
//   - data-mq-boot: el piso arranca apagado y se enciende en ola al montar,
//   - --mq-phase: desfase mínimo de las franjas al hacer scroll (como caminar sobre el piso).
// Todo lo que depende de movimiento se omite con prefers-reduced-motion.
// Además: teclado de pestañas (flechas, Inicio, Fin) con tabindex itinerante.
RVHProto.register("maiquetia", function (root) {
  "use strict";

  var ORDER = ["all", "accepts", "rejects", "unknown"];
  var motion = window.matchMedia("(prefers-reduced-motion: no-preference)");
  var tabs = Array.prototype.slice.call(root.querySelectorAll("[data-rvh-tab]"));
  var tablist = root.querySelector('[role="tablist"]');
  var empty = root.querySelector("[data-rvh-empty]");
  var prev = root.dataset.status || "all";
  var raf = 0;

  function syncTabs() {
    tabs.forEach(function (t) {
      t.tabIndex = t.getAttribute("aria-selected") === "true" ? 0 : -1;
    });
  }

  function onApplied(e) {
    var next = e.detail.state.status;
    if (next !== prev) {
      root.dataset.mqDir = ORDER.indexOf(next) < ORDER.indexOf(prev) ? "rtl" : "ltr";
      prev = next;
    }
    root.dataset.mqEmpty = e.detail.visible === 0 ? "1" : "0";
    syncTabs();
  }

  function onKey(e) {
    var i = tabs.indexOf(document.activeElement);
    if (i < 0) return;
    var target = null;
    if (e.key === "ArrowRight") target = tabs[(i + 1) % tabs.length];
    else if (e.key === "ArrowLeft") target = tabs[(i - 1 + tabs.length) % tabs.length];
    else if (e.key === "Home") target = tabs[0];
    else if (e.key === "End") target = tabs[tabs.length - 1];
    if (!target) return;
    // Evita que la barra del prototipo interprete ← → como cambio de variante.
    e.preventDefault();
    e.stopPropagation();
    target.focus();
    target.click();
  }

  function paintPhase() {
    raf = 0;
    root.style.setProperty("--mq-phase", Math.round(window.scrollY * -0.25) + "px");
  }

  function onScroll() {
    if (!raf && motion.matches) raf = window.requestAnimationFrame(paintPhase);
  }

  root.addEventListener("rvh:applied", onApplied);
  tablist.addEventListener("keydown", onKey);
  window.addEventListener("scroll", onScroll, { passive: true });

  root.dataset.mqDir = "ltr";
  root.dataset.mqEmpty = empty && !empty.hidden ? "1" : "0";
  syncTabs();

  if (motion.matches) {
    root.dataset.mqBoot = "1";
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { delete root.dataset.mqBoot; });
    });
  }

  return function () {
    root.removeEventListener("rvh:applied", onApplied);
    tablist.removeEventListener("keydown", onKey);
    window.removeEventListener("scroll", onScroll);
    if (raf) window.cancelAnimationFrame(raf);
    root.style.removeProperty("--mq-phase");
    delete root.dataset.mqDir;
    delete root.dataset.mqEmpty;
    delete root.dataset.mqBoot;
  };
});
