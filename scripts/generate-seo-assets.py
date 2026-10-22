# ruff: noqa: INP001
"""Regenerate the binary SEO assets in static/ (favicon.ico, apple-touch-icon.png, og.png).

Run with: .venv/bin/python scripts/generate-seo-assets.py
Needs Playwright's Chromium (already installed for the E2E tests).
"""

from __future__ import annotations

import struct
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

STATIC = Path(__file__).resolve().parents[1] / "static"
FLAG = (STATIC / "favicon.svg").read_text(encoding="utf-8")
FONT = (STATIC / "fonts" / "barlowcondensed-800-latin.woff2").as_uri()
BODY_FONT = (STATIC / "fonts" / "barlow-500-latin.woff2").as_uri()

OG_HTML = f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: BC; font-weight: 800; src: url("{FONT}"); }}
@font-face {{ font-family: B; font-weight: 500; src: url("{BODY_FONT}"); }}
html, body {{ margin: 0; width: 1200px; height: 630px; background: #0D1B3D; overflow: hidden; }}
.wrap {{ box-sizing: border-box; width: 1200px; height: 630px; padding: 72px 80px;
  display: flex; flex-direction: column; justify-content: space-between; color: #fff;
  border-left: 18px solid #FFCC00; }}
.brand {{ display: flex; align-items: center; gap: 24px; font: 800 38px/1 BC; letter-spacing: .12em;
  text-transform: uppercase; color: #C9D5EE; }}
.brand svg {{ width: 84px; height: 84px; }}
h1 {{ margin: 0; font: 800 118px/.92 BC; text-transform: uppercase; letter-spacing: .004em; }}
h1 em {{ font-style: normal; color: #FFCC00; }}
.foot {{ display: flex; justify-content: space-between; align-items: baseline;
  font: 500 34px/1 B; color: #C9D5EE; }}
.foot b {{ font: 800 44px/1 BC; letter-spacing: .08em; color: #fff; }}
</style><div class="wrap">
<div class="brand">{FLAG}<span>Remote Venezuela Hiring</span></div>
<h1>Empresas que contratan remoto desde <em>Venezuela</em></h1>
<div class="foot"><span>Directorio comunitario y abierto</span><b>contrataenve.com</b></div>
</div>"""

ICON_HTML = f"""<!doctype html><meta charset="utf-8"><style>
html, body {{ margin: 0; width: 180px; height: 180px; background: #0D1B3D; }}
svg {{ position: absolute; inset: 30px; width: 120px; height: 120px; }}
</style>{FLAG}"""


def write_ico(png: bytes, path: Path) -> None:
    """Wrap a 32x32 PNG in a single-image ICO container."""
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(png), 22)
    path.write_bytes(header + entry + png)


def main() -> None:
    with sync_playwright() as pw, tempfile.TemporaryDirectory() as tmp:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        og_page = Path(tmp) / "og.html"
        og_page.write_text(OG_HTML, encoding="utf-8")
        page.goto(og_page.as_uri())  # file:// page so the local @font-face URLs resolve
        page.evaluate("document.fonts.ready")
        page.screenshot(path=str(STATIC / "og.png"))

        page.set_viewport_size({"width": 180, "height": 180})
        page.set_content(ICON_HTML)
        page.screenshot(path=str(STATIC / "apple-touch-icon.png"))

        page.set_viewport_size({"width": 32, "height": 32})
        page.set_content(
            f"<style>html,body{{margin:0;background:transparent}}svg{{width:32px;height:32px}}</style>{FLAG}"
        )
        write_ico(page.screenshot(omit_background=True), STATIC / "favicon.ico")
        browser.close()


if __name__ == "__main__":
    main()
