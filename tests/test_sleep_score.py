import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sleep_score_route_returns_200_and_expected_score():
    payload = {
        "total_sleep_minutes": 420.0,
        "sleep_efficiency": 0.85,
        "snore_event_count": 2,
        "posture_change_count": 12,
    }
    response = client.post("/sleep_score", json=payload)
    assert response.status_code == 200
    assert response.json() == {"score": 91.0}


def test_sleep_score_route_ignores_snore_and_posture_counts():
    base_payload = {
        "total_sleep_minutes": 420.0,
        "sleep_efficiency": 0.85,
        "snore_event_count": 0,
        "posture_change_count": 0,
    }
    varied_payload = {
        "total_sleep_minutes": 420.0,
        "sleep_efficiency": 0.85,
        "snore_event_count": 45,
        "posture_change_count": 30,
    }

    base_response = client.post("/sleep_score", json=base_payload)
    varied_response = client.post("/sleep_score", json=varied_payload)

    assert base_response.status_code == 200
    assert varied_response.status_code == 200
    assert base_response.json()["score"] == 91.0
    assert base_response.json()["score"] == varied_response.json()["score"]


@pytest.mark.parametrize(
    "invalid_payload,field_name",
    [
        (
            {
                "total_sleep_minutes": -10.0,
                "sleep_efficiency": 0.85,
                "snore_event_count": 2,
                "posture_change_count": 12,
            },
            "total_sleep_minutes",
        ),
        (
            {
                "total_sleep_minutes": 420.0,
                "sleep_efficiency": 1.5,
                "snore_event_count": 2,
                "posture_change_count": 12,
            },
            "sleep_efficiency",
        ),
        (
            {
                "total_sleep_minutes": 420.0,
                "sleep_efficiency": -0.1,
                "snore_event_count": 2,
                "posture_change_count": 12,
            },
            "sleep_efficiency",
        ),
        (
            {
                "total_sleep_minutes": 420.0,
                "sleep_efficiency": 0.85,
                "snore_event_count": -1,
                "posture_change_count": 12,
            },
            "snore_event_count",
        ),
        (
            {
                "total_sleep_minutes": 420.0,
                "sleep_efficiency": 0.85,
                "snore_event_count": 2,
                "posture_change_count": -5,
            },
            "posture_change_count",
        ),
    ],
)
def test_validation_errors_return_422(invalid_payload, field_name):
    response = client.post("/sleep_score", json=invalid_payload)
    assert response.status_code == 422

    errors = response.json().get("detail", [])
    error_locs = [loc for err in errors for loc in err.get("loc", [])]
    assert field_name in error_locs