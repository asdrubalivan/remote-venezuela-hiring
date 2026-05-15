"""Playwright fixtures: build the site once per session and serve it on a
local HTTP server so tests can hit real ``http://`` URLs (file:// URLs break
relative ``href`` resolution and some browser behaviors)."""

from __future__ import annotations

import http.server
import socket
import socketserver
import threading
from pathlib import Path

import pytest

from remote_venezuela_hiring.build_site import build


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args, **kwargs):  # noqa: D401 - silence stdout
        pass


@pytest.fixture(scope="session")
def site_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("rvh-site")
    build(output_dir=out)
    return out


@pytest.fixture(scope="session")
def base_url(site_dir: Path):
    port = _free_port()

    class _Handler(_QuietHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(site_dir), **kw)

    httpd = socketserver.TCPServer(("127.0.0.1", port), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
