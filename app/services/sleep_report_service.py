from app.api.models.sleep_report import SleepReportRequest, SleepReportResponse


def generate_sleep_report(request: SleepReportRequest) -> SleepReportResponse:
    return SleepReportResponse(
        summary="Sleep report placeholder.",
        insights=[],
        recommendations=[],
    )