# ---- Unit 6 / B-1: API latency measurement over real HTTP ----
# Measures end-to-end response time of the three endpoints that determine
# the perceived responsiveness of the tool for an older adult:
#   POST /api/login          (authentication)
#   POST /api/responses      (validation + scoring + flag evaluation + DB write)
#   GET  /api/responses      (history + trend + flag for the dashboard)
#
# The measurement runs against a live development server so that the
# numbers include Flask routing, JSON (de)serialization, JWT verification,
# and SQLite I/O, which a test-client measurement would partly bypass.
#
# Usage:
#   1. Start the backend:  cd src/backend && flask --app app run --port 5000
#   2. From the repo root: python scripts/measure_latency.py
#
# The script registers its own throwaway user (lat_probe), grants consent,
# then times ITERATIONS requests per endpoint and reports mean / median /
# 95th percentile in milliseconds.
#
# Only the Python standard library is used, so the script runs in the same
# environment as the application itself with no extra installation.

import json
import statistics
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:5000"
ITERATIONS = 100
USERNAME = "lat_probe"
PASSWORD = "Passw0rd!probe"


def percentile_95(samples):
    ordered = sorted(samples)
    index = max(0, int(round(0.95 * len(ordered))) - 1)
    return ordered[index]


def request(method, path, payload=None, token=None, timeout=10):
    """Send one JSON request and return (status, parsed body)."""
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read().decode()
            return res.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as err:
        body = err.read().decode()
        return err.code, (json.loads(body) if body else {})


def timed(method, path, payload=None, token=None):
    """Time one request end to end and fail loudly on an error status."""
    start = time.perf_counter()
    status, body = request(method, path, payload, token)
    elapsed_ms = (time.perf_counter() - start) * 1000
    if status >= 400:
        sys.exit(f"{method} {path} failed: HTTP {status} {body}")
    return elapsed_ms, body


def main():
    # ---- Setup: health check, throwaway user, consent ----
    try:
        status, _ = request("GET", "/api/health", timeout=5)
    except OSError:
        sys.exit(f"Backend not reachable at {BASE_URL}. "
                 "Start it with: flask --app app run --port 5000")
    if status != 200:
        sys.exit(f"health check failed: HTTP {status}")

    status, body = request("POST", "/api/register", {
        "username": USERNAME, "password": PASSWORD,
        "role": "older_adult", "display_name": "Latency Probe",
    })
    if status not in (201, 409):  # 409 = already registered
        sys.exit(f"registration failed: HTTP {status} {body}")

    _, body = request("POST", "/api/login", {
        "username": USERNAME, "password": PASSWORD,
    })
    token = body["token"]

    request("POST", "/api/consent", token=token)

    # ---- Measurement ----
    results = {}

    samples = []
    for _ in range(ITERATIONS):
        elapsed, _ = timed("POST", "/api/login", {
            "username": USERNAME, "password": PASSWORD,
        })
        samples.append(elapsed)
    results["POST /api/login"] = samples

    samples = []
    for i in range(ITERATIONS):
        answers = {"q1": 1 + i % 3, "q2": 1 + (i // 3) % 3, "q3": 2}
        elapsed, _ = timed("POST", "/api/responses", answers, token=token)
        samples.append(elapsed)
    results["POST /api/responses"] = samples

    samples = []
    for _ in range(ITERATIONS):
        elapsed, _ = timed("GET", "/api/responses", token=token)
        samples.append(elapsed)
    results["GET /api/responses"] = samples

    # ---- Report ----
    print("=" * 66)
    print("API latency measurement (Unit 6, Part B-1)")
    print(f"target={BASE_URL}  iterations/endpoint={ITERATIONS}  "
          "transport=HTTP (urllib)")
    print("=" * 66)
    print()
    print(f"  {'endpoint':<22} {'mean':>8} {'median':>8} {'p95':>8}   (ms)")
    print(f"  {'-' * 22} {'-' * 8} {'-' * 8} {'-' * 8}")
    for endpoint, samples in results.items():
        print(f"  {endpoint:<22} "
              f"{statistics.mean(samples):>8.1f} "
              f"{statistics.median(samples):>8.1f} "
              f"{percentile_95(samples):>8.1f}")
    print()
    print("Note: POST /api/responses includes input validation (M3), "
          "scoring (M4),\nSQLite write (M5), and trend/flag evaluation (M6) "
          "in a single request.")


if __name__ == "__main__":
    main()
