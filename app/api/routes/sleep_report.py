from fastapi import APIRouter

from app.api.models.sleep_report import SleepReportRequest, SleepReportResponse
from app.services.sleep_report_service import generate_sleep_report

router = APIRouter()


@router.post("/sleep_report", response_model=SleepReportResponse)
def compute_sleep_report(request: SleepReportRequest) -> SleepReportResponse:
    return generate_sleep_report(request)