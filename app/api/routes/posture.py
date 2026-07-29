from fastapi import APIRouter

from app.api.models.posture import PostureRequest, PostureResponse
from app.services.posture_service import classify_posture

router = APIRouter()


@router.post("/posture", response_model=PostureResponse)
def compute_posture(request: PostureRequest) -> PostureResponse:
    return classify_posture(request)