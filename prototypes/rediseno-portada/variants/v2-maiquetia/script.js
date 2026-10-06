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
// El teclado de las pestañas lo pone proto.js.
RVHProto.register("maiquetia", function (root) {
  "use strict";

  var ORDER = ["all", "accepts", "rejects", "unknown"];
  var motion = window.matchMedia("(prefers-reduced-motion: no-preference)");
  var prev = root.dataset.status || "all";
  var raf = 0;

  function onApplied(e) {
    var next = e.detail.state.status;
    if (next !== prev) {
      root.dataset.mqDir = ORDER.indexOf(next) < ORDER.indexOf(prev) ? "rtl" : "ltr";
      prev = next;
    }
    root.dataset.mqEmpty = e.detail.visible === 0 ? "1" : "0";
  }

  function paintPhase() {
    raf = 0;
    root.style.setProperty("--mq-phase", Math.round(window.scrollY * -0.25) + "px");
  }

  function onScroll() {
    if (!raf && motion.matches) raf = window.requestAnimationFrame(paintPhase);
  }

  // proto.js vuelve a emitir "rvh:applied" justo después de montar el gancho,
  // así que el estado inicial (incluido el vacío) llega por onApplied.
  root.addEventListener("rvh:applied", onApplied);
  window.addEventListener("scroll", onScroll, { passive: true });
  root.dataset.mqDir = "ltr";

  if (motion.matches) {
    root.dataset.mqBoot = "1";
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () { delete root.dataset.mqBoot; });
    });
  }

  return function () {
    root.removeEventListener("rvh:applied", onApplied);
    window.removeEventListener("scroll", onScroll);
    if (raf) window.cancelAnimationFrame(raf);
    root.style.removeProperty("--mq-phase");
    delete root.dataset.mqDir;
    delete root.dataset.mqEmpty;
    delete root.dataset.mqBoot;
  };
});
