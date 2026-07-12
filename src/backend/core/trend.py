# ---- M6 Trend & Risk Flag (isolated core logic) ----
# Evaluates a user's score time series and decides whether a risk flag
# should fire. Design decision from Unit 1 peer review (carried through
# the Unit 3 design): the flag is TREND-LINKED. A single high score never
# fires a flag, because loneliness is a fluctuating state and one-off
# spikes may be transient. Only sustained high scores or a worsening
# trajectory fire the flag.
#
# Pure functions over a list of scores (oldest first). Thresholds are
# module-level constants so they stay isolated and testable, and can be
# tuned after sensitivity/specificity checks on simulated trajectories
# (stable / worsening / improving), as planned in the Unit 3 report.

from .scoring import HIGH_SCORE_CUTOFF

# Number of most recent assessments considered by the flag logic.
WINDOW_SIZE = 3

# Minimum total increase across the window to count as worsening.
WORSENING_MIN_INCREASE = 2

FLAG_NONE = "none"
FLAG_SUSTAINED_HIGH = "sustained_high"
FLAG_WORSENING = "worsening"


def trend_direction(scores: list) -> str:
    """Classify the direction of the recent window: rising, falling, stable."""
    window = scores[-WINDOW_SIZE:]
    if len(window) < 2:
        return "stable"
    delta = window[-1] - window[0]
    if delta >= 1:
        return "rising"
    if delta <= -1:
        return "falling"
    return "stable"


def evaluate_flag(scores: list) -> dict:
    """Decide the risk flag for a score history (oldest first).

    Returns {"level": <flag>, "reason": <short explanation>}.
    Rules, in priority order:
      1. Fewer than WINDOW_SIZE scores: never flag (not enough evidence).
      2. Sustained high: every score in the window at or above the cutoff.
      3. Worsening: total increase across the window >= WORSENING_MIN_INCREASE
         and the last TWO scores both at or above the cutoff, so elevation
         has persisted across consecutive assessments.
      4. Otherwise: no flag. A single spike does not fire.
    """
    if len(scores) < WINDOW_SIZE:
        return {
            "level": FLAG_NONE,
            "reason": f"fewer than {WINDOW_SIZE} assessments",
        }

    window = scores[-WINDOW_SIZE:]

    if all(score >= HIGH_SCORE_CUTOFF for score in window):
        return {
            "level": FLAG_SUSTAINED_HIGH,
            "reason": (
                f"last {WINDOW_SIZE} scores all at or above "
                f"{HIGH_SCORE_CUTOFF}"
            ),
        }

    increase = window[-1] - window[0]
    persisted = all(
        score >= HIGH_SCORE_CUTOFF for score in window[-2:]
    )
    if increase >= WORSENING_MIN_INCREASE and persisted:
        return {
            "level": FLAG_WORSENING,
            "reason": (
                f"score rose by {increase} across the last {WINDOW_SIZE} "
                f"assessments and stayed at or above {HIGH_SCORE_CUTOFF} "
                f"for two consecutive assessments"
            ),
        }

    return {"level": FLAG_NONE, "reason": "no sustained or worsening pattern"}
