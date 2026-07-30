from fastapi import APIRouter, HTTPException, status

from app.api.models.sleep_report import SleepReportRequest, SleepReportResponse
from app.services.sleep_report_service import (
    SleepReportServiceTimeoutError,
    SleepReportServiceUnavailableError,
    SleepReportServiceUpstreamError,
    generate_sleep_report,
)

router = APIRouter()


@router.post(
    "/sleep_report",
    response_model=SleepReportResponse,
    status_code=status.HTTP_200_OK,
)
def create_sleep_report(request: SleepReportRequest) -> SleepReportResponse:
    """Generates an AI-driven sleep analysis report from biometric metrics."""
    try:
        return generate_sleep_report(request)
    except SleepReportServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Sleep report generation timed out. Please try again later.",
        ) from exc
    except SleepReportServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sleep report service is currently unavailable.",
        ) from exc
    except SleepReportServiceUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to receive a valid report from the AI provider.",
        ) from exc