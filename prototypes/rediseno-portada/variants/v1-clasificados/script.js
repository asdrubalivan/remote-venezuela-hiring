// PROTOTIPO — v1 Clasificados: el bolígrafo.
// Al activar la pestaña "Acepta" se encierran en rojo, uno tras otro, los Status de
// las primeras filas visibles; al activar "No acepta" se tachan. El resto de la
// lista ya aparece marcado (lo resuelve el CSS con #stage[data-status]).
// Con prefers-reduced-motion no se anima nada: todo se ve ya dibujado.
RVHProto.register("clasificados", function (root) {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var MAX_ANIMATED = 10;
  var STEP_MS = 85;
  var lastStatus = root.dataset.status || "all";

  function draw(status) {
    if (reduce.matches) return;
    var selector = status === "accepts" ? ".pen--circle" : ".pen--strike";
    var viewport = window.innerHeight || document.documentElement.clientHeight;
    var k = 0;
    root.querySelectorAll("[data-rvh-row]:not([hidden]) " + selector).forEach(function (pen) {
      pen.classList.remove("is-drawing");
      if (k >= MAX_ANIMATED) return;
      var box = pen.getBoundingClientRect(); // fuerza el reflow para reiniciar la animación
      if (box.bottom < 0 || box.top > viewport) return;
      pen.style.setProperty("--pen-delay", 60 + k * STEP_MS + "ms");
      pen.classList.add("is-drawing");
      k++;
    });
  }

  function onApplied(e) {
    var status = e.detail.state.status;
    if (status !== lastStatus && (status === "accepts" || status === "rejects")) draw(status);
    lastStatus = status;
  }

  function onDone(e) {
    var pen = e.target && e.target.closest ? e.target.closest(".pen.is-drawing") : null;
    if (pen) pen.classList.remove("is-drawing");
  }

  root.addEventListener("rvh:applied", onApplied);
  root.addEventListener("animationend", onDone);
  root.addEventListener("animationcancel", onDone);
  if (lastStatus === "accepts" || lastStatus === "rejects") draw(lastStatus);

  return function () {
    root.removeEventListener("rvh:applied", onApplied);
    root.removeEventListener("animationend", onDone);
    root.removeEventListener("animationcancel", onDone);
  };
});
