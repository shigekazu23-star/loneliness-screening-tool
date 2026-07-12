# ---- M4 Scoring (isolated core logic) ----
# Computes the loneliness score from the Three-Item Loneliness Scale
# (Hughes et al., 2004). Pure function: no I/O, no framework imports,
# following the onion/clean separation defined in the Unit 3 design.

# Each item is answered on a 3-point scale:
#   1 = hardly ever, 2 = some of the time, 3 = often
ITEM_KEYS = ("q1", "q2", "q3")
MIN_ITEM = 1
MAX_ITEM = 3
MIN_SCORE = 3
MAX_SCORE = 9

# Commonly used cutoff: total score >= 6 indicates elevated loneliness.
HIGH_SCORE_CUTOFF = 6


class InvalidResponseError(ValueError):
    """Raised when questionnaire answers fail validation (M3 contract)."""


def validate_answers(answers: dict) -> dict:
    """Validate raw answers and return a clean {q1, q2, q3} dict of ints."""
    clean = {}
    for key in ITEM_KEYS:
        if key not in answers:
            raise InvalidResponseError(f"missing item: {key}")
        try:
            value = int(answers[key])
        except (TypeError, ValueError):
            raise InvalidResponseError(f"item {key} is not an integer")
        if not MIN_ITEM <= value <= MAX_ITEM:
            raise InvalidResponseError(
                f"item {key} out of range {MIN_ITEM}-{MAX_ITEM}: {value}"
            )
        clean[key] = value
    return clean


def compute_score(answers: dict) -> int:
    """Sum the three validated items into a total score (3-9)."""
    clean = validate_answers(answers)
    return sum(clean[key] for key in ITEM_KEYS)


def is_high(score: int) -> bool:
    """Whether a single score is at or above the elevated-loneliness cutoff."""
    return score >= HIGH_SCORE_CUTOFF
