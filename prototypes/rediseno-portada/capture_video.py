# ruff: noqa: INP001, T201  (PROTOTIPO descartable: scripts de consola)
"""PROTOTIPO — material para el video de Remotion.

Por cada variante deja en ``video/public/shots/vN/``:
  desktop-long.png  1440 de ancho (DPR 2), los primeros 2600 px de la página
  mobile-long.png   390 de ancho (DPR 3), los primeros 2200 px
  sig/NNN.jpg       la animación firma cuadro a cuadro (1440x900, DPR 1.5, 30 fps)

La animación firma se captura de forma determinista: se congela la línea de
tiempo de animaciones con CDP, se dispara la acción (clic en una pestaña) y se
avanza cada animación a mano con ``currentTime``.

Uso: .venv/bin/python prototypes/rediseno-portada/capture_video.py [--only N] [--actual]
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

from remote_venezuela_hiring.build_site import build as build_site

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import VARIANTS, build
from shoot import _serve

PUBLIC = Path(__file__).resolve().parent / "video" / "public" / "shots"
FPS = 30
SIG_MS = 1400
LEAD_FRAMES = 8

# Acción que dispara la firma de cada variante: (tipo, valor, bajar hasta las pestañas).
SIG: dict[int, tuple[str, str, bool]] = {
    1: ("tab", "accepts", True),
    2: ("tab", "rejects", False),  # la banda de franjas vive arriba
    3: ("tab", "rejects", True),
    4: ("tab", "rejects", True),
    5: ("letter", "M", True),  # el índice de letras
}
# Recorrido simulado del salto por letra (v5), en ms.
JUMP_MS = 600


def _settle(page: Page) -> None:
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(600)


def _ease_out_expo(x: float) -> float:
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def _signature(page: Page, n: int, out: Path) -> dict[str, object]:
    out.mkdir(parents=True, exist_ok=True)
    kind, value, scroll_to_tabs = SIG[n]
    if scroll_to_tabs:
        page.evaluate(
            """() => {
              const tabs = document.querySelector('[role="tablist"]');
              const y = tabs ? tabs.getBoundingClientRect().top + scrollY - 220 : 0;
              window.scrollTo(0, Math.max(0, y));
            }"""
        )
    page.wait_for_timeout(500)
    sig_scroll = page.evaluate("scrollY")
    for i in range(LEAD_FRAMES):
        page.screenshot(path=str(out / f"{i:03d}.jpg"), type="jpeg", quality=90)

    selector = f'[data-rvh-tab="{value}"]' if kind == "tab" else f'[data-guia-letter="{value}"]'
    target = page.locator(selector).first
    box = target.bounding_box() or {"x": 720, "y": 450, "width": 0, "height": 0}
    click = {"x": box["x"] + box["width"] / 2, "y": box["y"] + box["height"] / 2}

    if kind == "letter":
        # Salto instantáneo y sin temporizadores largos: el recorrido se dibuja a mano.
        page.evaluate(
            """() => {
              const st = window.setTimeout.bind(window);
              window.setTimeout = (fn, ms, ...a) => (ms >= 1000 ? 0 : st(fn, ms, ...a));
              const orig = Element.prototype.scrollIntoView;
              Element.prototype.scrollIntoView = function (o) {
                orig.call(this, Object.assign({}, o, { behavior: "instant" }));
              };
            }"""
        )
    cdp = page.context.new_cdp_session(page)
    cdp.send("Animation.enable")
    cdp.send("Animation.setPlaybackRate", {"playbackRate": 0})
    target.click()
    page.wait_for_timeout(1500)
    end_scroll = page.evaluate("scrollY")
    count = page.evaluate(
        "() => { const a = document.getAnimations(); a.forEach(x => x.pause()); return a.length; }"
    )
    frames = SIG_MS * FPS // 1000
    for f in range(frames):
        t = f * 1000 / FPS
        anim_t = t
        if kind == "letter":
            k = _ease_out_expo(min(1.0, t / JUMP_MS))
            page.evaluate(
                "y => window.scrollTo({ top: y, behavior: 'instant' })",
                sig_scroll + (end_scroll - sig_scroll) * k,
            )
            anim_t = max(0.0, t - JUMP_MS)
        page.evaluate(
            "t => document.getAnimations().forEach(a => { a.currentTime = t; })",
            anim_t,
        )
        page.screenshot(path=str(out / f"{LEAD_FRAMES + f:03d}.jpg"), type="jpeg", quality=90)
    print(f"[capture] v{n}: {count} animaciones, {LEAD_FRAMES + frames} cuadros")
    return {"sigFrames": LEAD_FRAMES + frames, "click": click, "sigScroll": sig_scroll}


def _current_site(browser: Browser) -> None:
    """Captura la portada actual (para la intro del video)."""
    with tempfile.TemporaryDirectory() as tmp:
        build_site(output_dir=Path(tmp))
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page.goto((Path(tmp) / "index.html").as_uri(), wait_until="networkidle")
        _settle(page)
        PUBLIC.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(PUBLIC / "actual-desktop.png"))
        page.close()
    print("[capture] portada actual")


def main() -> None:
    only = int(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    build()
    httpd, port = _serve()
    manifest: dict[str, object] = {}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            if "--actual" in sys.argv or not (PUBLIC / "actual-desktop.png").exists():
                _current_site(browser)
            for v in VARIANTS:
                n = int(v["n"])  # type: ignore[call-overload]
                if only and n != only:
                    continue
                vdir = PUBLIC / f"v{n}"
                if vdir.exists():
                    shutil.rmtree(vdir)
                vdir.mkdir(parents=True)
                url = f"http://127.0.0.1:{port}/?v={n}&bar=0"

                page = browser.new_page(
                    viewport={"width": 1440, "height": 900}, device_scale_factor=2
                )
                page.goto(url, wait_until="networkidle")
                _settle(page)
                h = min(2600, page.evaluate("document.documentElement.scrollHeight"))
                page.screenshot(
                    path=str(vdir / "desktop-long.png"),
                    full_page=True,
                    clip={"x": 0, "y": 0, "width": 1440, "height": h},
                )
                page.close()

                page = browser.new_page(
                    viewport={"width": 390, "height": 844}, device_scale_factor=3
                )
                page.goto(url, wait_until="networkidle")
                _settle(page)
                mh = min(2200, page.evaluate("document.documentElement.scrollHeight"))
                page.screenshot(
                    path=str(vdir / "mobile-long.png"),
                    full_page=True,
                    clip={"x": 0, "y": 0, "width": 390, "height": mh},
                )
                page.close()

                page = browser.new_page(
                    viewport={"width": 1440, "height": 900}, device_scale_factor=1.5
                )
                page.goto(url, wait_until="networkidle")
                _settle(page)
                sig = _signature(page, n, vdir / "sig")
                page.close()

                manifest[f"v{n}"] = {
                    "name": v["name"],
                    "desktopHeight": h,
                    "mobileHeight": mh,
                    "sigLeadFrames": LEAD_FRAMES,
                    **sig,
                }
            browser.close()
    finally:
        httpd.shutdown()

    mpath = PUBLIC / "manifest.json"
    old = json.loads(mpath.read_text()) if mpath.exists() else {}
    old.update(manifest)
    mpath.write_text(json.dumps(old, indent=2, ensure_ascii=False))
    print(f"[capture] manifiesto: {mpath}")


if __name__ == "__main__":
    main()
