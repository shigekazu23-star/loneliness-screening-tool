# ---- End-to-end test fixtures ----
# Starts a throwaway backend (Flask on an isolated SQLite file) and serves the
# production frontend build, so the browser exercises the same artifact that a
# deployment would ship. Each session gets a fresh database, which keeps the
# acceptance scenarios independent of any data left by manual use.
#
# Run:  python -m pytest tests/e2e -v
# The frontend must be built first:  cd src/frontend && npm run build

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(REPO_ROOT, "src", "backend")
FRONTEND_DIST = os.path.join(REPO_ROOT, "src", "frontend", "dist")

BACKEND_PORT = 5055
FRONTEND_PORT = 5056
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"


def _wait_for(url: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2):
                return
        except Exception as err:  # noqa: BLE001 - any failure means not ready
            last = err
            time.sleep(0.4)
    raise RuntimeError(f"{url} did not become ready: {last}")


def _free(port: int) -> bool:
    with socket.socket() as sock:
        return sock.connect_ex(("127.0.0.1", port)) != 0


@pytest.fixture(scope="session")
def backend():
    """Run the Flask API against a temporary database for the whole session."""
    if not _free(BACKEND_PORT):
        raise RuntimeError(f"port {BACKEND_PORT} is already in use")

    tmp_dir = tempfile.mkdtemp(prefix="lst_e2e_")
    env = dict(os.environ)
    env["LST_DB_PATH"] = os.path.join(tmp_dir, "e2e.db")
    env["LST_JWT_SECRET"] = "e2e-only-secret-not-for-production"

    proc = subprocess.Popen(
        [sys.executable, "-m", "flask", "--app", "app", "run",
         "--port", str(BACKEND_PORT)],
        cwd=BACKEND_DIR, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    try:
        _wait_for(f"{BACKEND_URL}/api/health")
        # Seed the three demo trajectories plus the caregiver account.
        subprocess.run([sys.executable, "seed_simulation.py"],
                       cwd=BACKEND_DIR, env=env, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        yield BACKEND_URL
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def frontend(backend):
    """Serve the production build and proxy /api to the test backend."""
    if not os.path.isdir(FRONTEND_DIST):
        pytest.skip("frontend build missing; run 'npm run build' in src/frontend")

    dist = FRONTEND_DIST
    backend_url = backend

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=dist, **kwargs)

        def log_message(self, *args):  # keep pytest output readable
            pass

        def _proxy(self, method):
            from urllib.error import HTTPError
            from urllib.request import Request, urlopen as _open

            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None
            req = Request(f"{backend_url}{self.path}", data=body, method=method)
            for header in ("Content-Type", "Authorization"):
                if self.headers.get(header):
                    req.add_header(header, self.headers[header])
            try:
                with _open(req, timeout=15) as res:
                    payload, status = res.read(), res.status
            except HTTPError as err:
                payload, status = err.read(), err.code
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            if self.path.startswith("/api/"):
                return self._proxy("GET")
            # Single-page app: unknown paths fall back to index.html.
            if not os.path.exists(os.path.join(dist, self.path.lstrip("/"))):
                self.path = "/index.html"
            return super().do_GET()

        def do_POST(self):
            return self._proxy("POST")

        def do_DELETE(self):
            return self._proxy("DELETE")

    server = ThreadingHTTPServer(("127.0.0.1", FRONTEND_PORT), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        _wait_for(FRONTEND_URL)
        yield FRONTEND_URL
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture
def app_page(page, frontend):
    """A browser page with the application loaded and a clean session."""
    page.goto(frontend)
    page.evaluate("() => sessionStorage.clear()")
    page.goto(frontend)
    return page
