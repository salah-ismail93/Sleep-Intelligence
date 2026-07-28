from fastapi import APIRouter
from app.api.models.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def get_health_status() -> HealthResponse:
    return HealthResponse(status="healthy")
