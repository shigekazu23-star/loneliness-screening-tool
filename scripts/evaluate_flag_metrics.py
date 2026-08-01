# ---- Unit 6 / B-1: reliability evaluation of the trend-linked risk flag ----
# Measures classification performance (sensitivity, specificity, PPV, NPV)
# of core.trend.evaluate_flag against 250 simulated score trajectories:
# 5 controlled patterns x 50 noisy replicates each, with a fixed RNG seed
# so every run reproduces the same numbers (reproducibility requirement).
#
# Ground truth is the generative pattern, following the Unit 3 design:
#   should flag      : worsening, sustained_high
#   should NOT flag  : stable_low, improving, transient_spike
# The transient_spike class directly tests the Unit 1 design decision that
# a single high score must never fire the flag on its own.
#
# A trajectory is predicted POSITIVE if the flag fires at least once while
# replaying the assessments in order (the same procedure the running
# application uses after every questionnaire submission).
#
# Usage (from the repo root):
#   python scripts/evaluate_flag_metrics.py

import os
import random
import sys

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "src", "backend"),
)

from core import scoring, trend  # noqa: E402

SEED = 42
REPLICATES_PER_PATTERN = 50
NOISE_PROBABILITY = 0.3  # chance that each item is perturbed by +/-1

# Base answer trajectories (q1, q2, q3 per assessment, 5 assessments).
# stable_low / worsening / improving mirror the seeder trajectories used
# since Unit 4; sustained_high and transient_spike complete the design
# space of the flag rules.
PATTERNS = {
    "stable_low": {
        "label": 0,
        "answers": [(1, 1, 2), (1, 2, 1), (2, 1, 1), (1, 1, 2), (1, 2, 1)],
    },
    # NOTE (evaluation design finding): an earlier version of this base
    # started at 8 -> 7 -> 6, i.e. three consecutive scores at or above
    # the cutoff. The flag then fired in 72% of replicates, which is
    # CORRECT behaviour (a sustained-high episode preceding the
    # improvement), not a false positive. The base was therefore steepened
    # so that no 3-assessment window is entirely at or above the cutoff,
    # keeping the "should NOT flag" label truthful. The original finding
    # is reported in the Unit 6 Discussion.
    "improving": {
        "label": 0,
        "answers": [(3, 2, 2), (2, 2, 2), (2, 2, 1), (2, 1, 1), (1, 1, 1)],
    },
    "transient_spike": {
        "label": 0,
        "answers": [(1, 1, 2), (1, 2, 1), (3, 3, 3), (1, 1, 2), (1, 2, 1)],
    },
    "worsening": {
        "label": 1,
        "answers": [(1, 1, 2), (2, 2, 1), (2, 2, 2), (3, 2, 2), (3, 3, 2)],
    },
    "sustained_high": {
        "label": 1,
        "answers": [(2, 2, 2), (2, 3, 2), (3, 2, 2), (2, 2, 3), (3, 3, 2)],
    },
}


def perturb(base_answers, rng):
    """Return a noisy copy of a base trajectory (item-level +/-1 noise)."""
    noisy = []
    for triple in base_answers:
        items = []
        for value in triple:
            if rng.random() < NOISE_PROBABILITY:
                value += rng.choice((-1, 1))
            items.append(max(scoring.MIN_ITEM, min(scoring.MAX_ITEM, value)))
        noisy.append(tuple(items))
    return noisy


def flag_fires(answer_trajectory) -> bool:
    """Replay assessments in order; True if the flag fires at any point."""
    history = []
    for q1, q2, q3 in answer_trajectory:
        score = scoring.compute_score({"q1": q1, "q2": q2, "q3": q3})
        history.append(score)
        if trend.evaluate_flag(history)["level"] != trend.FLAG_NONE:
            return True
    return False


def compute_results() -> dict:
    """Run the full evaluation and return counts and metrics.

    Kept separate from the report printing so that other scripts (for
    example the Part B-3 figure generator) reuse the exact same numbers
    from a single source of truth.
    """
    rng = random.Random(SEED)
    tp = fp = tn = fn = 0
    per_pattern = {}

    for name, spec in PATTERNS.items():
        fired = 0
        for _ in range(REPLICATES_PER_PATTERN):
            predicted = flag_fires(perturb(spec["answers"], rng))
            fired += predicted
            if spec["label"] == 1 and predicted:
                tp += 1
            elif spec["label"] == 1 and not predicted:
                fn += 1
            elif spec["label"] == 0 and predicted:
                fp += 1
            else:
                tn += 1
        per_pattern[name] = fired

    return {
        "per_pattern": per_pattern,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "sensitivity": tp / (tp + fn),
        "specificity": tn / (tn + fp),
        "ppv": tp / (tp + fp),
        "npv": tn / (tn + fn),
    }


def main():
    results = compute_results()
    per_pattern = results["per_pattern"]
    tp, fp = results["tp"], results["fp"]
    tn, fn = results["tn"], results["fn"]
    total = tp + fp + tn + fn
    sensitivity = results["sensitivity"]
    specificity = results["specificity"]
    ppv = results["ppv"]
    npv = results["npv"]

    print("=" * 62)
    print("Risk-flag reliability evaluation (Unit 6, Part B-1)")
    print(f"seed={SEED}  replicates/pattern={REPLICATES_PER_PATTERN}  "
          f"noise p={NOISE_PROBABILITY}  n={total}")
    print("=" * 62)
    print()
    print("Flag fire rate by simulated pattern (ground truth in brackets):")
    for name, spec in PATTERNS.items():
        truth = "should flag" if spec["label"] else "should NOT flag"
        rate = per_pattern[name] / REPLICATES_PER_PATTERN
        print(f"  {name:<16} [{truth:<15}]  fired {per_pattern[name]:>2}/"
              f"{REPLICATES_PER_PATTERN}  ({rate:.0%})")
    print()
    print("Confusion matrix (positive = flag fired at least once):")
    print(f"                     predicted +   predicted -")
    print(f"  actual + (n={tp + fn:>3})   TP = {tp:<8} FN = {fn}")
    print(f"  actual - (n={tn + fp:>3})   FP = {fp:<8} TN = {tn}")
    print()
    print("Classification metrics:")
    print(f"  Sensitivity (recall)             : {sensitivity:.3f}")
    print(f"  Specificity                      : {specificity:.3f}")
    print(f"  Positive predictive value (PPV)  : {ppv:.3f}")
    print(f"  Negative predictive value (NPV)  : {npv:.3f}")


if __name__ == "__main__":
    main()
