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

import statistics
import sys
import time

import requests

BASE_URL = "http://127.0.0.1:5000"
ITERATIONS = 100
USERNAME = "lat_probe"
PASSWORD = "Passw0rd!probe"


def percentile_95(samples):
    ordered = sorted(samples)
    index = max(0, int(round(0.95 * len(ordered))) - 1)
    return ordered[index]


def timed(method, url, **kwargs):
    start = time.perf_counter()
    response = method(url, timeout=10, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.raise_for_status()
    return elapsed_ms, response


def main():
    # ---- Setup: health check, throwaway user, consent ----
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=5).raise_for_status()
    except requests.RequestException:
        sys.exit(f"Backend not reachable at {BASE_URL}. "
                 "Start it with: flask --app app run --port 5000")

    register = requests.post(f"{BASE_URL}/api/register", json={
        "username": USERNAME, "password": PASSWORD,
        "role": "older_adult", "display_name": "Latency Probe",
    }, timeout=10)
    if register.status_code not in (201, 409):  # 409 = already registered
        sys.exit(f"registration failed: {register.status_code} {register.text}")

    token = requests.post(f"{BASE_URL}/api/login", json={
        "username": USERNAME, "password": PASSWORD,
    }, timeout=10).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    requests.post(f"{BASE_URL}/api/consent", headers=headers, timeout=10)

    # ---- Measurement ----
    results = {}

    samples = []
    for _ in range(ITERATIONS):
        elapsed, _ = timed(requests.post, f"{BASE_URL}/api/login", json={
            "username": USERNAME, "password": PASSWORD,
        })
        samples.append(elapsed)
    results["POST /api/login"] = samples

    samples = []
    for i in range(ITERATIONS):
        answers = {"q1": 1 + i % 3, "q2": 1 + (i // 3) % 3, "q3": 2}
        elapsed, _ = timed(requests.post, f"{BASE_URL}/api/responses",
                           json=answers, headers=headers)
        samples.append(elapsed)
    results["POST /api/responses"] = samples

    samples = []
    for _ in range(ITERATIONS):
        elapsed, _ = timed(requests.get, f"{BASE_URL}/api/responses",
                           headers=headers)
        samples.append(elapsed)
    results["GET /api/responses"] = samples

    # ---- Report ----
    print("=" * 66)
    print("API latency measurement (Unit 6, Part B-1)")
    print(f"target={BASE_URL}  iterations/endpoint={ITERATIONS}  "
          "transport=HTTP (requests)")
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
