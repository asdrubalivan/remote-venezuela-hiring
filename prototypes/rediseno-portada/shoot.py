# ruff: noqa: INP001, T201  (PROTOTIPO descartable: scripts de consola)
"""PROTOTIPO — capturas de las variantes (escritorio y móvil) con Playwright.

Uso:
  .venv/bin/python prototypes/rediseno-portada/shoot.py            # todas
  .venv/bin/python prototypes/rediseno-portada/shoot.py --only 3   # solo la v3

Construye out/ primero y deja las capturas en shots/:
  vN-desktop.png (1440 de ancho, primer viewport), vN-desktop-full.png,
  vN-mobile.png (390 de ancho, primer viewport), vN-mobile-full.png
"""

from __future__ import annotations

import functools
import http.server
import socket
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import OUT, VARIANTS, build

SHOTS = Path(__file__).resolve().parent / "shots"


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args: object, **kwargs: object) -> None:
        pass


def _serve() -> tuple[socketserver.TCPServer, int]:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    httpd = socketserver.TCPServer(
        ("127.0.0.1", port), functools.partial(_Quiet, directory=str(OUT))
    )
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def main() -> None:
    only = int(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    build()
    SHOTS.mkdir(exist_ok=True)
    httpd, port = _serve()
    viewports = {"desktop": (1440, 900, 1), "mobile": (390, 844, 2)}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for v in VARIANTS:
                if only and v["n"] != only:
                    continue
                for label, (w, h, scale) in viewports.items():
                    page = browser.new_page(
                        viewport={"width": w, "height": h}, device_scale_factor=scale
                    )
                    page.emulate_media(reduced_motion="reduce")
                    page.goto(
                        f"http://127.0.0.1:{port}/?v={v['n']}&bar=0", wait_until="networkidle"
                    )
                    page.evaluate("document.fonts.ready")
                    page.wait_for_timeout(400)
                    base = SHOTS / f"v{v['n']}-{label}"
                    page.screenshot(path=f"{base}.png")
                    page.screenshot(path=f"{base}-full.png", full_page=True)
                    page.close()
                print(f"[shoot] v{v['n']} {v['name']} listo")
            browser.close()
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
