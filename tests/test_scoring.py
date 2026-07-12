# ---- Tests for M4 Scoring (core logic, no I/O) ----

import pytest

from core import scoring


def test_minimum_score():
    assert scoring.compute_score({"q1": 1, "q2": 1, "q3": 1}) == 3


def test_maximum_score():
    assert scoring.compute_score({"q1": 3, "q2": 3, "q3": 3}) == 9


def test_mixed_answers():
    assert scoring.compute_score({"q1": 2, "q2": 1, "q3": 3}) == 6


def test_string_digits_are_accepted():
    assert scoring.compute_score({"q1": "2", "q2": "2", "q3": "2"}) == 6


def test_missing_item_rejected():
    with pytest.raises(scoring.InvalidResponseError):
        scoring.validate_answers({"q1": 1, "q2": 1})


def test_out_of_range_rejected():
    with pytest.raises(scoring.InvalidResponseError):
        scoring.validate_answers({"q1": 0, "q2": 2, "q3": 2})
    with pytest.raises(scoring.InvalidResponseError):
        scoring.validate_answers({"q1": 4, "q2": 2, "q3": 2})


def test_non_integer_rejected():
    with pytest.raises(scoring.InvalidResponseError):
        scoring.validate_answers({"q1": "often", "q2": 2, "q3": 2})


def test_high_cutoff():
    assert scoring.is_high(6) is True
    assert scoring.is_high(5) is False
