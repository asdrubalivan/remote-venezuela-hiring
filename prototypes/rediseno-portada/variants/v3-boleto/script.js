// PROTOTIPO — v3 Boleto. El gesto firma: al cambiar de pestaña, filtro o búsqueda,
// los sellos de los primeros cupones visibles se estampan una vez, escalonados.
// El resto de los cupones ya está estampado: el sello es visible por defecto y,
// con prefers-reduced-motion, nunca se anima.
(function () {
  "use strict";

  var MAX_SELLOS = 8;

  window.RVHProto.register("boleto", function (root) {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
    var timer = 0;
    var raf = 0;

    function filtroDom(nombre) {
      var s = root.querySelector('[data-rvh-filter="' + nombre + '"]');
      return s ? s.value : "all";
    }

    // Estado inicial leído del DOM: proto.js aplica el estado antes de registrar el gancho.
    var q = root.querySelector("[data-rvh-search]");
    var a = root.querySelector("[data-rvh-archived]");
    var ultimaBusqueda = q ? q.value.trim().toLowerCase() : "";
    var ultimoResto = [root.dataset.status || "all", filtroDom("method"), filtroDom("platform"),
      filtroDom("tag"), a && a.checked ? 1 : 0].join("|");

    function estampar() {
      if (reduce.matches) return;
      Array.prototype.forEach.call(root.querySelectorAll(".is-stamping"), function (f) {
        f.classList.remove("is-stamping");
      });
      var alto = window.innerHeight;
      var filas = root.querySelectorAll("[data-rvh-row]:not([hidden])");
      var n = 0;
      for (var i = 0; i < filas.length && n < MAX_SELLOS; i++) {
        var r = filas[i].getBoundingClientRect();
        if (r.bottom <= 0) continue;
        if (r.top >= alto) break;
        filas[i].style.setProperty("--bo-i", String(n));
        void filas[i].offsetWidth; // reinicia la animación si ya estaba estampando
        filas[i].classList.add("is-stamping");
        n++;
      }
    }

    function alAplicar(e) {
      var s = e.detail.state;
      var resto = [s.status, s.method, s.platform, s.tag, s.archived ? 1 : 0].join("|");
      var cambioBusqueda = s.search !== ultimaBusqueda;
      if (resto === ultimoResto && !cambioBusqueda) return; // ordenar no vuelve a sellar
      var soloBusqueda = resto === ultimoResto;
      ultimoResto = resto;
      ultimaBusqueda = s.search;
      window.clearTimeout(timer);
      // al teclear se espera una pausa breve para no sellar en cada letra
      timer = window.setTimeout(estampar, soloBusqueda ? 220 : 0);
    }

    function alTerminar(e) {
      var fila = e.target.closest ? e.target.closest("[data-rvh-row]") : null;
      if (!fila) return;
      var ultima = fila.querySelector(".bo-mini--stale") ? "bo-estampar-mini" : "bo-estampar";
      if (e.animationName === ultima) fila.classList.remove("is-stamping");
    }

    root.addEventListener("rvh:applied", alAplicar);
    root.addEventListener("animationend", alTerminar);
    // primer montaje: el talonario llega sellando
    raf = window.requestAnimationFrame(estampar);

    return function () {
      window.clearTimeout(timer);
      window.cancelAnimationFrame(raf);
      root.removeEventListener("rvh:applied", alAplicar);
      root.removeEventListener("animationend", alTerminar);
    };
  });
})();
