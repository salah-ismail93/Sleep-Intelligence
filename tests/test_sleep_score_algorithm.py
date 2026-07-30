import math

import pytest

from app.algorithms.scoring.sleep_score import calculate_sleep_score


def test_confirmed_reference_example_returns_91():
    assert calculate_sleep_score(420.0, 0.85) == 91.0


def test_duration_credit_is_capped_at_420_minutes():
    assert calculate_sleep_score(840.0, 0.85) == 91.0


def test_partial_duration_and_efficiency_are_weighted():
    assert calculate_sleep_score(210.0, 0.50) == 50.0


def test_result_is_rounded_to_one_decimal_place():
    assert calculate_sleep_score(300.0, 0.823) == 78.0


@pytest.mark.parametrize(
    "total_sleep_minutes,sleep_efficiency",
    [
        (-1.0, 0.85),
        (math.nan, 0.85),
        (math.inf, 0.85),
        (420.0, -0.01),
        (420.0, 1.01),
        (420.0, math.nan),
        (420.0, math.inf),
    ],
)
def test_invalid_inputs_are_rejected(total_sleep_minutes, sleep_efficiency):
    with pytest.raises(ValueError):
        calculate_sleep_score(total_sleep_minutes, sleep_efficiency)
