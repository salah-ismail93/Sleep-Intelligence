from app.api.models.sleep_score import SleepScoreRequest, SleepScoreResponse


def calculate_sleep_score(request: SleepScoreRequest) -> SleepScoreResponse:
    return SleepScoreResponse(score=0.0)