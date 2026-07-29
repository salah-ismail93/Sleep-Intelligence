from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_valid_sleep_score_request_returns_200_and_placeholder():
    payload = {
        "total_sleep_minutes": 480.0,
        "sleep_efficiency": 0.85,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }

    response = client.post("/sleep_score", json=payload)

    assert response.status_code == 200
    assert response.json() == {"score": 0.0}


def test_invalid_efficiency_outside_range_returns_422():
    payload = {
        "total_sleep_minutes": 480.0,
        "sleep_efficiency": 1.5,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }

    response = client.post("/sleep_score", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field,invalid_value",
    [
        ("snore_event_count", -1),
        ("posture_change_count", -1),
    ],
)
def test_negative_event_or_posture_counts_return_422(field: str, invalid_value: int):
    payload = {
        "total_sleep_minutes": 480.0,
        "sleep_efficiency": 0.85,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }
    payload[field] = invalid_value

    response = client.post("/sleep_score", json=payload)

    assert response.status_code == 422


def test_negative_sleep_duration_returns_422():
    payload = {
        "total_sleep_minutes": -10.0,
        "sleep_efficiency": 0.85,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }

    response = client.post("/sleep_score", json=payload)

    assert response.status_code == 422