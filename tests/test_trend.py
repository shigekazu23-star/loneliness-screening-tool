# ---- Tests for M6 Trend & Risk Flag (core logic, no I/O) ----
# Reliability check requested in the Unit 2 instructor feedback and
# planned in the Unit 3 report: the flag is validated against controlled
# simulated trajectories (stable / worsening / improving) and must not
# fire on a single high score.

from core import trend

STABLE = [4, 4, 5, 4, 4]
WORSENING = [4, 5, 6, 7, 8]
IMPROVING = [8, 7, 6, 5, 4]
SINGLE_SPIKE = [4, 4, 8]
SUSTAINED_HIGH = [7, 7, 8]


def test_stable_trajectory_never_flags():
    for end in range(1, len(STABLE) + 1):
        assert trend.evaluate_flag(STABLE[:end])["level"] == trend.FLAG_NONE


def test_worsening_trajectory_flags():
    assert trend.evaluate_flag(WORSENING)["level"] in (
        trend.FLAG_WORSENING,
        trend.FLAG_SUSTAINED_HIGH,
    )


def test_improving_trajectory_never_flags():
    assert trend.evaluate_flag(IMPROVING)["level"] == trend.FLAG_NONE


def test_single_spike_does_not_flag():
    # Core design decision from Unit 1 peer review: one-off high scores
    # must not fire the flag.
    assert trend.evaluate_flag(SINGLE_SPIKE)["level"] == trend.FLAG_NONE


def test_sustained_high_flags():
    assert (
        trend.evaluate_flag(SUSTAINED_HIGH)["level"]
        == trend.FLAG_SUSTAINED_HIGH
    )


def test_too_few_assessments_never_flag():
    assert trend.evaluate_flag([])["level"] == trend.FLAG_NONE
    assert trend.evaluate_flag([9])["level"] == trend.FLAG_NONE
    assert trend.evaluate_flag([9, 9])["level"] == trend.FLAG_NONE


def test_trend_direction():
    assert trend.trend_direction([4, 5, 7]) == "rising"
    assert trend.trend_direction([7, 5, 4]) == "falling"
    assert trend.trend_direction([5, 6, 5]) == "stable"
    assert trend.trend_direction([5]) == "stable"
