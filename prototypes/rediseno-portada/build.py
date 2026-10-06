# ruff: noqa: INP001, T201  (PROTOTIPO descartable: scripts de consola)
"""PROTOTIPO — rediseño de la portada en 5 variantes. Código descartable.

Renderiza las 5 variantes con los datos y textos reales en ``out/index.html``.
Cada variante vive en ``variants/vN-slug/`` (markup.html, style.css, fonts.url
y opcionalmente script.js). Se cambia de variante con ``?v=1..5`` o con la
barra flotante. Ver README.md.

Uso:  .venv/bin/python prototypes/rediseno-portada/build.py [--serve]
"""

from __future__ import annotations

import functools
import html
import http.server
import re
import shutil
import socketserver
import sys
from datetime import UTC, datetime
from pathlib import Path

from jinja2 import ChoiceLoader, FileSystemLoader

from remote_venezuela_hiring.build_site import TEMPLATES_DIR, _index_context, _make_env
from remote_venezuela_hiring.load_data import load_all_companies

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
PORT = 8090

VARIANTS: list[dict[str, object]] = [
    {"n": 1, "slug": "clasificados", "name": "Clasificados"},
    {"n": 2, "slug": "maiquetia", "name": "Piso de Maiquetía"},
    {"n": 3, "slug": "boleto", "name": "Boleto"},
    {"n": 4, "slug": "metro", "name": "Metro"},
    {"n": 5, "slug": "guia", "name": "Guía amarilla"},
]

# Textos visibles de la portada actual. Cada variante debe conservarlos todos.
REQUIRED_COPY: list[str] = [
    "Saltar al contenido",
    "Remote Venezuela",
    "Hiring",
    "Empresas",
    "Estadísticas",
    "Ajustes de visualización",
    "Tema",
    "Densidad de la tabla",
    "Cómoda",
    "Compacta",
    "GitHub",
    "Compatibilidad de Contratación Remota en",
    "Base de datos pública, mantenida por la comunidad, de empresas que pueden "
    "aceptar candidatos remotos desde Venezuela.",
    "probablemente aceptan",
    "actualizado",
    "No es asesoramiento legal ni una declaración oficial de ninguna empresa.",
    "La compatibilidad puede cambiar — siempre verifica directamente.",
    "Contribuir en GitHub",
    "Buscar empresas, etiquetas...",
    "Filtros",
    "Verificación: Todas",
    "Plataforma: Todas",
    "Etiqueta: Todas",
    "Mostrar archivadas",
    "Limpiar",
    "Todas",
    "Acepta",
    "No acepta",
    "Desconocido",
    "Empresa",
    "Estado",
    "Últ. verificación",
    "Verificación",
    "Plataforma",
    "Etiquetas",
    "Probablemente acepta Venezuela",
    "Reportada como no aceptante",
    "Desconocido / necesita revisión",
    "DESACT.",
    "Ninguna empresa coincide con los filtros.",
    "Limpiar filtros",
    "Agregar empresa vía GitHub Issues",
    "Enviar un pull request YAML",
    "Reportar datos incorrectos",
    "Generado el",
    "Código fuente en GitHub",
    "Contribuye con una entrada",
]


def _variant_dir(v: dict[str, object]) -> Path:
    return HERE / "variants" / f"v{v['n']}-{v['slug']}"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _check_copy(rendered: str) -> list[str]:
    text = re.sub(r"\s+", " ", html.unescape(rendered))
    return [s for s in REQUIRED_COPY if s not in text]


def build() -> Path:
    companies = load_all_companies()
    env = _make_env(TEMPLATES_DIR)
    env.loader = ChoiceLoader([FileSystemLoader(str(HERE)), FileSystemLoader(str(TEMPLATES_DIR))])

    ctx: dict[str, object] = {
        "companies": companies,
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        **_index_context(companies),
    }

    variants: list[dict[str, object]] = []
    failures = 0
    for v in VARIANTS:
        vdir = _variant_dir(v)
        rel = vdir.relative_to(HERE).as_posix()
        markup = env.get_template(f"{rel}/markup.html").render(**ctx)
        missing = _check_copy(markup)
        if missing:
            failures += 1
            print(f"[copy] v{v['n']} {v['name']}: faltan {missing}", file=sys.stderr)
        variants.append(
            {
                **v,
                "markup": markup,
                "css": _read(vdir / "style.css"),
                "js": _read(vdir / "script.js"),
                "fonts": _read(vdir / "fonts.url").strip(),
            }
        )

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    page = env.get_template("shell.html").render(
        variants=variants,
        variant_meta=[{k: v[k] for k in ("n", "slug", "name")} for v in variants],
        proto_css=_read(HERE / "proto.css"),
        proto_js=_read(HERE / "proto.js"),
    )
    index = OUT / "index.html"
    index.write_text(page, encoding="utf-8")
    print(f"[proto] {index} ({len(variants)} variantes, {failures} con textos faltantes)")
    return index


def serve() -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"[proto] http://127.0.0.1:{PORT}/?v=1  (Ctrl+C para salir)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
