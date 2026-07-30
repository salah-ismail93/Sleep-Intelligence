import pytest
from fastapi.testclient import TestClient

from app.api.models.sleep_report import SleepReportResponse
from app.main import app
from app.services.sleep_report_service import (
    SleepReportServiceTimeoutError,
    SleepReportServiceUnavailableError,
    SleepReportServiceUpstreamError,
)

client = TestClient(app)

SECRET_KEY_EXPOSURE_TEST = "secret-gemini-api-key-998877"


@pytest.fixture
def valid_payload():
    return {
        "total_sleep_minutes": 480.0,
        "sleep_efficiency": 0.85,
        "sleep_score": 88.5,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }


def test_valid_sleep_report_request_returns_200_and_generated_report(
    valid_payload, monkeypatch
):
    expected_response = SleepReportResponse(
        summary="The supplied data shows total sleep of 480 minutes with 0.85 efficiency.",
        insights=["Detected posture changes and snore counts are observational metrics."],
        recommendations=["Maintain consistent sleep schedules for optimal rest."],
    )

    monkeypatch.setattr(
        "app.api.routes.sleep_report.generate_sleep_report",
        lambda req: expected_response,
    )

    response = client.post("/sleep_report", json=valid_payload)

    assert response.status_code == 200
    assert response.json() == expected_response.model_dump()


def test_sleep_report_timeout_maps_to_504_and_hides_secrets(
    valid_payload, monkeypatch
):
    def mock_timeout(req):
        raise SleepReportServiceTimeoutError(
            f"Upstream provider timeout with key={SECRET_KEY_EXPOSURE_TEST}"
        )

    monkeypatch.setattr(
        "app.api.routes.sleep_report.generate_sleep_report",
        mock_timeout,
    )

    response = client.post("/sleep_report", json=valid_payload)

    assert response.status_code == 504
    assert SECRET_KEY_EXPOSURE_TEST not in response.text
    assert "Upstream provider timeout" not in response.text


def test_sleep_report_unavailable_maps_to_503_and_hides_secrets(
    valid_payload, monkeypatch
):
    def mock_unavailable(req):
        raise SleepReportServiceUnavailableError(
            f"Provider connection error using auth key={SECRET_KEY_EXPOSURE_TEST}"
        )

    monkeypatch.setattr(
        "app.api.routes.sleep_report.generate_sleep_report",
        mock_unavailable,
    )

    response = client.post("/sleep_report", json=valid_payload)

    assert response.status_code == 503
    assert SECRET_KEY_EXPOSURE_TEST not in response.text
    assert "Provider connection error" not in response.text


def test_sleep_report_upstream_error_maps_to_502_and_hides_secrets(
    valid_payload, monkeypatch
):
    def mock_upstream(req):
        raise SleepReportServiceUpstreamError(
            f"Malformed provider JSON payload containing key={SECRET_KEY_EXPOSURE_TEST}"
        )

    monkeypatch.setattr(
        "app.api.routes.sleep_report.generate_sleep_report",
        mock_upstream,
    )

    response = client.post("/sleep_report", json=valid_payload)

    assert response.status_code == 502
    assert SECRET_KEY_EXPOSURE_TEST not in response.text
    assert "Malformed provider JSON" not in response.text


@pytest.mark.parametrize(
    "invalid_payload,field_name",
    [
        (
            {
                "total_sleep_minutes": -10,
                "sleep_efficiency": 0.85,
                "sleep_score": 88.5,
                "snore_event_count": 2,
                "posture_change_count": 12,
            },
            "total_sleep_minutes",
        ),
        (
            {
                "total_sleep_minutes": 480,
                "sleep_efficiency": 1.5,
                "sleep_score": 88.5,
                "snore_event_count": 2,
                "posture_change_count": 12,
            },
            "sleep_efficiency",
        ),
        (
            {
                "total_sleep_minutes": 480,
                "sleep_efficiency": -0.1,
                "sleep_score": 88.5,
                "snore_event_count": 2,
                "posture_change_count": 12,
            },
            "sleep_efficiency",
        ),
        (
            {
                "total_sleep_minutes": 480,
                "sleep_efficiency": 0.85,
                "sleep_score": 150.0,
                "snore_event_count": 2,
                "posture_change_count": 12,
            },
            "sleep_score",
        ),
        (
            {
                "total_sleep_minutes": 480,
                "sleep_efficiency": 0.85,
                "sleep_score": -5.0,
                "snore_event_count": 2,
                "posture_change_count": 12,
            },
            "sleep_score",
        ),
        (
            {
                "total_sleep_minutes": 480,
                "sleep_efficiency": 0.85,
                "sleep_score": 88.5,
                "snore_event_count": -1,
                "posture_change_count": 12,
            },
            "snore_event_count",
        ),
        (
            {
                "total_sleep_minutes": 480,
                "sleep_efficiency": 0.85,
                "sleep_score": 88.5,
                "snore_event_count": 2,
                "posture_change_count": -3,
            },
            "posture_change_count",
        ),
    ],
)
def test_validation_errors_return_422(invalid_payload, field_name):
    response = client.post("/sleep_report", json=invalid_payload)
    assert response.status_code == 422
    
    # Assert that the targeted invalid field name is listed in the 422 error detail locations
    errors = response.json().get("detail", [])
    error_locs = [loc for err in errors for loc in err.get("loc", [])]
    assert field_name in error_locs