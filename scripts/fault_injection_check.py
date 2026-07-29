# ---- Fault injection: does the test suite actually detect a regression? ----
# A suite that always passes proves nothing on its own. This script verifies
# that the tests have real detection power by deliberately introducing a fault
# into the screening logic, running the suite, and confirming that the fault is
# caught. The original file is always restored, including if the run fails.
#
# The injected fault raises the elevated-loneliness cutoff from 6 to 8, which
# would silently stop the flag from firing for genuinely at-risk users. It is
# exactly the kind of change that must never reach production unnoticed.
#
# Usage (from the repo root):
#   python scripts/fault_injection_check.py            # unit + integration
#   python scripts/fault_injection_check.py --with-e2e # also run the browser tests

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TARGET = os.path.join(REPO_ROOT, "src", "backend", "core", "scoring.py")

ORIGINAL = "HIGH_SCORE_CUTOFF = 6"
INJECTED = "HIGH_SCORE_CUTOFF = 8  # FAULT INJECTED FOR TESTING"


def run_suite(with_e2e: bool):
    args = [sys.executable, "-m", "pytest", "tests", "-q"]
    if not with_e2e:
        args += ["--ignore=tests/e2e"]
    return subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-e2e", action="store_true",
                        help="include the browser-driven acceptance tests")
    opts = parser.parse_args()

    source = open(TARGET, encoding="utf-8").read()
    if ORIGINAL not in source:
        sys.exit(f"expected to find {ORIGINAL!r} in {TARGET}")

    backup = tempfile.mktemp(suffix=".py")
    shutil.copy2(TARGET, backup)

    print("=" * 68)
    print("Fault injection check (Unit 7, Part A)")
    print("=" * 68)
    print(f"target        : src/backend/core/scoring.py")
    print(f"fault         : {ORIGINAL}  ->  HIGH_SCORE_CUTOFF = 8")
    print(f"meaning       : the elevated-loneliness threshold is raised, so the")
    print(f"                risk flag would stay silent for at-risk users")
    print(f"scope         : {'unit + integration + acceptance' if opts.with_e2e else 'unit + integration'}")
    print()

    try:
        open(TARGET, "w", encoding="utf-8").write(
            source.replace(ORIGINAL, INJECTED)
        )
        print("--- running the suite against the faulty code ---")
        result = run_suite(opts.with_e2e)
        tail = [ln for ln in result.stdout.splitlines() if ln.strip()][-6:]
        for line in tail:
            print("   ", line)
        detected = result.returncode != 0
    finally:
        shutil.copy2(backup, TARGET)
        os.remove(backup)
        restored = open(TARGET, encoding="utf-8").read()
        assert ORIGINAL in restored and "FAULT INJECTED" not in restored
        print()
        print("--- original file restored and verified ---")

    print()
    if detected:
        print("RESULT: PASS - the suite detected the injected fault.")
        print("The tests therefore have real regression-detection power; a silent")
        print("change to the screening threshold cannot reach main unnoticed.")
    else:
        print("RESULT: FAIL - the suite did NOT detect the injected fault.")
        print("This would mean the threshold is untested. Add a test before relying")
        print("on the suite as a safety net.")
    return 0 if detected else 1


if __name__ == "__main__":
    sys.exit(main())
