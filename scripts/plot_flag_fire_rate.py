# ---- Unit 6 / B-3: figure for the flag reliability evaluation ----
# Draws a bar chart of the flag fire rate per simulated trajectory
# pattern, colored by ground truth (should flag / should not flag).
# One figure communicates both sides of the reliability story:
# sensitivity (right two bars near 100%) and specificity (left three
# bars near 0%), including the "a single spike never fires" design
# decision (transient_spike at 10%).
#
# Numbers come from evaluate_flag_metrics.compute_results() so the
# chart can never drift from the reported table (single source of
# truth, fixed RNG seed).
#
# Palette (validated for CVD separation and contrast, light surface):
#   #2E5FA3 blue  = ground-truth negative (should NOT flag)
#   #B57E2F amber = ground-truth positive (should flag)
# Redundant encoding: hatching on the positive bars plus direct value
# labels, so the distinction never relies on color alone.
#
# Usage (from the repo root):
#   python scripts/plot_flag_fire_rate.py
# Output:
#   docs/figures/flag_fire_rate.png (300 dpi, for the Word documents)

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))

from evaluate_flag_metrics import (  # noqa: E402
    PATTERNS,
    REPLICATES_PER_PATTERN,
    compute_results,
)

COLOR_NEGATIVE = "#2E5FA3"  # should NOT flag
COLOR_POSITIVE = "#B57E2F"  # should flag
SURFACE = "#FFFFFF"

DISPLAY_NAMES = {
    "stable_low": "Stable low",
    "improving": "Improving",
    "transient_spike": "Transient\nspike",
    "worsening": "Worsening",
    "sustained_high": "Sustained\nhigh",
}

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "docs", "figures", "flag_fire_rate.png"
)


def main():
    results = compute_results()
    names = list(PATTERNS.keys())
    rates = [
        100 * results["per_pattern"][name] / REPLICATES_PER_PATTERN
        for name in names
    ]
    positives = [PATTERNS[name]["label"] == 1 for name in names]

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 11,
    })

    fig, ax = plt.subplots(figsize=(6.5, 3.9), dpi=300)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    bars = ax.bar(
        range(len(names)),
        rates,
        width=0.62,
        color=[COLOR_POSITIVE if pos else COLOR_NEGATIVE for pos in positives],
        hatch=["//" if pos else "" for pos in positives],
        edgecolor=SURFACE,
        linewidth=1.5,
    )

    # Direct value labels (relief for any contrast limitation, and the
    # exact rates the text refers to).
    for bar, rate in zip(bars, rates):
        ax.annotate(
            f"{rate:.0f}%",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            color="#333333",
        )

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([DISPLAY_NAMES[name] for name in names])
    ax.set_ylabel("Flag fire rate (%)")
    ax.set_xlabel(
        f"Simulated trajectory pattern "
        f"(n = {REPLICATES_PER_PATTERN} noisy replicates each)"
    )
    ax.set_ylim(0, 112)
    ax.set_yticks(range(0, 101, 20))

    # Recessive grid and axes.
    ax.yaxis.grid(True, color="#DDDDDD", linewidth=0.6)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#999999")

    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, color=COLOR_NEGATIVE),
        plt.Rectangle(
            (0, 0), 1, 1,
            facecolor=COLOR_POSITIVE, hatch="//", edgecolor=SURFACE,
        ),
    ]
    ax.legend(
        legend_handles,
        ["Ground truth: should not flag", "Ground truth: should flag"],
        loc="upper left",
        frameon=False,
        fontsize=10,
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, facecolor=SURFACE, bbox_inches="tight")
    print(f"saved: {os.path.normpath(OUTPUT_PATH)}")
    print("sensitivity={sensitivity:.3f} specificity={specificity:.3f} "
          "ppv={ppv:.3f} npv={npv:.3f}".format(**results))


if __name__ == "__main__":
    main()
