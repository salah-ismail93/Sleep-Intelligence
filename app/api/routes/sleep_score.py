from fastapi import APIRouter

from app.api.models.sleep_score import SleepScoreRequest, SleepScoreResponse
from app.services.sleep_score_service import calculate_sleep_score

router = APIRouter()


@router.post("/sleep_score", response_model=SleepScoreResponse)
def compute_sleep_score(request: SleepScoreRequest) -> SleepScoreResponse:
    return calculate_sleep_score(request)