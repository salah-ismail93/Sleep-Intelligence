import math


MINUTES_FOR_FULL_DURATION_CREDIT = 420.0
DURATION_WEIGHT = 0.40
EFFICIENCY_WEIGHT = 0.60
MIN_SCORE = 0.0
MAX_SCORE = 100.0
SCORE_DECIMAL_PLACES = 1


def calculate_sleep_score(
    total_sleep_minutes: float,
    sleep_efficiency: float,
) -> float:
    """Calculate the Version 1 adult-oriented sleep-wellness heuristic."""
    if not math.isfinite(total_sleep_minutes) or total_sleep_minutes < 0.0:
        raise ValueError("total_sleep_minutes must be a finite, non-negative number.")
    if not math.isfinite(sleep_efficiency) or not 0.0 <= sleep_efficiency <= 1.0:
        raise ValueError("sleep_efficiency must be a finite number between 0.0 and 1.0.")

    duration_component = min(
        total_sleep_minutes / MINUTES_FOR_FULL_DURATION_CREDIT,
        1.0,
    ) * MAX_SCORE
    efficiency_component = sleep_efficiency * MAX_SCORE

    raw_score = (
        DURATION_WEIGHT * duration_component
        + EFFICIENCY_WEIGHT * efficiency_component
    )
    clamped_score = min(max(raw_score, MIN_SCORE), MAX_SCORE)
    return round(clamped_score, SCORE_DECIMAL_PLACES)
