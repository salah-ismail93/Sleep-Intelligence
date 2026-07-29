from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_valid_sleep_report_request_returns_200_and_placeholder():
    payload = {
        "total_sleep_minutes": 480.0,
        "sleep_efficiency": 0.85,
        "sleep_score": 88.5,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }

    response = client.post("/sleep_report", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "summary": "Sleep report placeholder.",
        "insights": [],
        "recommendations": [],
    }


def test_invalid_efficiency_returns_422():
    payload = {
        "total_sleep_minutes": 480.0,
        "sleep_efficiency": 1.2,  # Invalid: > 1.0
        "sleep_score": 88.5,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }

    response = client.post("/sleep_report", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("invalid_score", [-1.0, 105.0])
def test_invalid_sleep_score_returns_422(invalid_score: float):
    payload = {
        "total_sleep_minutes": 480.0,
        "sleep_efficiency": 0.85,
        "sleep_score": invalid_score,  # Invalid: outside [0.0, 100.0]
        "snore_event_count": 2,
        "posture_change_count": 12,
    }

    response = client.post("/sleep_report", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field,invalid_value",
    [
        ("total_sleep_minutes", -10.0),
        ("snore_event_count", -1),
        ("posture_change_count", -1),
    ],
)
def test_negative_duration_or_counts_return_422(field: str, invalid_value):
    payload = {
        "total_sleep_minutes": 480.0,
        "sleep_efficiency": 0.85,
        "sleep_score": 88.5,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }
    payload[field] = invalid_value

    response = client.post("/sleep_report", json=payload)

    assert response.status_code == 422