from app.algorithms.scoring.sleep_score import (
    calculate_sleep_score as calculate_score_algo,
)
from app.api.models.sleep_score import SleepScoreRequest, SleepScoreResponse


def calculate_sleep_score(request: SleepScoreRequest) -> SleepScoreResponse:
    """Calculates the adult-oriented Version 1 sleep score using only duration and efficiency."""
    result = calculate_score_algo(
        total_sleep_minutes=request.total_sleep_minutes,
        sleep_efficiency=request.sleep_efficiency,
    )
    return SleepScoreResponse(score=result)