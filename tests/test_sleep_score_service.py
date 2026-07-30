from app.api.models.sleep_score import SleepScoreRequest
from app.services.sleep_score_service import calculate_sleep_score


def test_reference_example_returns_expected_score():
    request = SleepScoreRequest(
        total_sleep_minutes=420.0,
        sleep_efficiency=0.85,
        snore_event_count=2,
        posture_change_count=12,
    )
    response = calculate_sleep_score(request)
    assert response.score == 91.0


def test_snore_and_posture_counts_do_not_affect_score():
    base_request = SleepScoreRequest(
        total_sleep_minutes=420.0,
        sleep_efficiency=0.85,
        snore_event_count=0,
        posture_change_count=0,
    )
    varied_request = SleepScoreRequest(
        total_sleep_minutes=420.0,
        sleep_efficiency=0.85,
        snore_event_count=50,
        posture_change_count=30,
    )

    base_response = calculate_sleep_score(base_request)
    varied_response = calculate_sleep_score(varied_request)

    assert base_response.score == 91.0
    assert base_response.score == varied_response.score