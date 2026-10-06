// PROTOTIPO — v4 Metro. Gesto firma: el diagrama de línea.
// Una línea vertical une las estaciones (filas) visibles, de la primera a la última.
// Al cambiar de pestaña o de filtro toma el color del Status activo (lo hace el CSS
// con #stage[data-status]) y se redibuja una vez de arriba hacia abajo, solo en el
// tramo que se ve en pantalla; las estaciones se encienden cuando la línea las alcanza.
// Con prefers-reduced-motion la línea se coloca sin animación.
RVHProto.register("metro", function (root) {
  "use strict";

  var board = root.querySelector("[data-metro-board]");
  var line = root.querySelector("[data-metro-line]");
  if (!board || !line) return null;

  var DURATION = 560;
  var EASE = "cubic-bezier(0.16, 1, 0.3, 1)";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var running = [];
  var lastKey = null;
  var alive = true;

  function stops() {
    return Array.prototype.slice.call(board.querySelectorAll("tr[data-rvh-row]:not([hidden]) .m-stop"));
  }

  function center(el, origin) {
    var r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2 - origin.left, y: r.top + r.height / 2 - origin.top };
  }

  // La línea sale del filete de la cabecera (borde superior del tbody, que no es
  // sticky) y termina en el centro de la última estación visible.
  var body = board.querySelector("tbody");
  function layout() {
    var list = stops();
    if (!list.length) {
      line.hidden = true;
      return null;
    }
    line.hidden = false;
    var origin = board.getBoundingClientRect();
    var first = center(list[0], origin);
    var last = center(list[list.length - 1], origin);
    var top = body ? body.getBoundingClientRect().top - origin.top : first.y;
    var height = Math.max(0, last.y - top);
    line.style.left = first.x + "px";
    line.style.top = top + "px";
    line.style.height = height + "px";
    return { top: top, height: height, origin: origin, stops: list };
  }

  function stopRunning() {
    running.forEach(function (a) { a.cancel(); });
    running = [];
  }

  // Inversa aproximada de la curva ease-out exponencial: en qué fracción del tiempo
  // la línea alcanza la fracción p del recorrido.
  function timeAt(p) {
    var k = 1 - Math.pow(2, -10);
    return Math.min(1, -Math.log(1 - p * k) / Math.LN2 / 10);
  }

  function draw() {
    stopRunning();
    var g = layout();
    if (!g || reduce.matches || !line.animate) return;
    var lineTop = g.origin.top + g.top; // y de la cabecera de línea en el viewport
    var from = Math.min(Math.max(-lineTop, 0), g.height);
    var to = Math.min(Math.max(window.innerHeight - lineTop, 0), g.height);
    if (to - from < 8) return;

    running.push(line.animate(
      [
        { clipPath: "inset(" + from + "px 0 " + (g.height - from) + "px 0)" },
        { clipPath: "inset(" + from + "px 0 " + (g.height - to) + "px 0)" },
      ],
      { duration: DURATION, easing: EASE }
    ));

    g.stops.forEach(function (stop) {
      var y = center(stop, g.origin).y - g.top;
      if (y < from || y > to) return;
      var delay = DURATION * timeAt((y - from) / (to - from));
      running.push(stop.animate(
        [
          { transform: "scale(0.25)", opacity: 0 },
          { transform: "scale(1.3)", opacity: 1, offset: 0.6 },
          { transform: "scale(1)", opacity: 1 },
        ],
        { duration: 260, delay: delay, easing: "ease-out", fill: "backwards" }
      ));
    });
  }

  function keyOf(s) {
    return [s.status, s.method, s.platform, s.tag, s.archived ? 1 : 0].join("|");
  }

  function onApplied(e) {
    var key = keyOf(e.detail.state);
    if (key !== lastKey) {
      lastKey = key;
      draw();
    } else {
      layout();
    }
  }

  root.addEventListener("rvh:applied", onApplied);

  var ro = "ResizeObserver" in window ? new ResizeObserver(function () { layout(); }) : null;
  if (ro) ro.observe(board);
  window.addEventListener("resize", layout);

  // Estado inicial leído del DOM (el hook se registra después del primer apply).
  function value(name) {
    var el = root.querySelector('[data-rvh-filter="' + name + '"]');
    return el ? el.value : "all";
  }
  var archived = root.querySelector("[data-rvh-archived]");
  lastKey = keyOf({
    status: root.dataset.status || "all",
    method: value("method"),
    platform: value("platform"),
    tag: value("tag"),
    archived: !!(archived && archived.checked),
  });

  // Primer trazo al montar, cuando las fuentes ya fijaron la altura de las filas.
  layout();
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(function () {
    if (alive) draw();
  });

  return function cleanup() {
    alive = false;
    stopRunning();
    root.removeEventListener("rvh:applied", onApplied);
    window.removeEventListener("resize", layout);
    if (ro) ro.disconnect();
  };
});
