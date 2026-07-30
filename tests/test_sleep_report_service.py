from unittest.mock import MagicMock
import pytest

from app.api.models.sleep_report import SleepReportRequest, SleepReportResponse
from app.config.settings import SettingsError
from app.integrations.gemini.exceptions import (
    GeminiAuthenticationError,
    GeminiConnectionError,
    GeminiIntegrationError,
    GeminiRateLimitError,
    GeminiResponseParseError,
    GeminiTimeoutError,
)
from app.services.sleep_report_service import (
    SleepReportServiceTimeoutError,
    SleepReportServiceUnavailableError,
    SleepReportServiceUpstreamError,
    generate_sleep_report,
)


@pytest.fixture
def valid_report_request():
    return SleepReportRequest(
        total_sleep_minutes=480,
        sleep_efficiency=0.85,
        sleep_score=88.5,
        snore_event_count=2,
        posture_change_count=12,
    )


def test_successful_structured_report(valid_report_request):
    mock_client = MagicMock()
    mock_data = {
        "summary": "The supplied data shows 8 hours of total sleep time with an efficiency score of 0.85.",
        "insights": ["Detected snore events (2) and posture changes (12) reflect raw sensor counts."],
        "recommendations": ["Maintain fixed sleep and wake schedules to preserve general sleep routine."],
    }
    mock_client.generate_structured_json.return_value = mock_data

    result = generate_sleep_report(
        request=valid_report_request,
        client_factory=lambda: mock_client,
    )

    assert isinstance(result, SleepReportResponse)
    assert result.summary == mock_data["summary"]
    assert result.insights == mock_data["insights"]
    assert result.recommendations == mock_data["recommendations"]


def test_request_data_correctly_formatted_in_prompt(valid_report_request):
    mock_client = MagicMock()
    mock_client.generate_structured_json.return_value = {
        "summary": "Data summary.",
        "insights": ["Data insight."],
        "recommendations": ["General recommendation."],
    }

    generate_sleep_report(
        request=valid_report_request,
        client_factory=lambda: mock_client,
    )

    mock_client.generate_structured_json.assert_called_once()
    call_kwargs = mock_client.generate_structured_json.call_args.kwargs
    prompt = call_kwargs["prompt"]
    schema = call_kwargs["response_schema"]

    # Verify exact labeled metric lines in the prompt
    assert "Total Sleep Time: 480.0 minutes" in prompt
    assert "Sleep Efficiency: 0.85" in prompt
    assert "Sleep Score: 88.5" in prompt
    assert "Snore Events: 2" in prompt
    assert "Posture Changes: 12" in prompt

    # Verify schema parameter passed to adapter
    assert schema == SleepReportResponse.model_json_schema()


def test_prompt_includes_scientific_safeguards_and_non_causal_instructions(valid_report_request):
    mock_client = MagicMock()
    mock_client.generate_structured_json.return_value = {
        "summary": "Valid summary",
        "insights": ["Valid insight"],
        "recommendations": ["Valid recommendation"],
    }

    generate_sleep_report(
        request=valid_report_request,
        client_factory=lambda: mock_client,
    )

    mock_client.generate_structured_json.assert_called_once()
    prompt = mock_client.generate_structured_json.call_args.kwargs["prompt"].lower()

    # Non-causal phrasing requirements
    assert "non-causal language" in prompt or "never claim definitive causation" in prompt
    assert "may be associated with" in prompt

    # Strictly forbidden clinical / unmeasured inferences
    assert "airway resistance" in prompt
    assert "breathing quality" in prompt
    assert "sleep architecture" in prompt or "stages" in prompt

    # Reference range and detector prohibitions
    assert "detector outputs" in prompt
    assert "do not label metrics as 'normal', 'healthy', or 'optimal'" in prompt

    # Limitation & Uncertainty acknowledgment
    assert "acknowledge uncertainty" in prompt


def test_service_configuration_error_mapping(valid_report_request):
    def failing_factory():
        raise SettingsError("Gemini API key is missing.")

    with pytest.raises(SleepReportServiceUnavailableError, match="misconfigured"):
        generate_sleep_report(
            request=valid_report_request,
            client_factory=failing_factory,
        )


def test_timeout_mapping(valid_report_request):
    mock_client = MagicMock()
    mock_client.generate_structured_json.side_effect = GeminiTimeoutError("Timed out")

    with pytest.raises(SleepReportServiceTimeoutError, match="timed out"):
        generate_sleep_report(
            request=valid_report_request,
            client_factory=lambda: mock_client,
        )


@pytest.mark.parametrize(
    "gemini_exception",
    [
        GeminiAuthenticationError("Bad Key"),
        GeminiRateLimitError("Quota Exceeded"),
        GeminiConnectionError("Network issue"),
    ],
)
def test_unavailable_service_exception_mapping(valid_report_request, gemini_exception):
    mock_client = MagicMock()
    mock_client.generate_structured_json.side_effect = gemini_exception

    with pytest.raises(SleepReportServiceUnavailableError, match="unavailable or misconfigured"):
        generate_sleep_report(
            request=valid_report_request,
            client_factory=lambda: mock_client,
        )


@pytest.mark.parametrize(
    "upstream_exception",
    [
        GeminiResponseParseError("Invalid JSON"),
        GeminiIntegrationError("Upstream failure"),
    ],
)
def test_upstream_error_mapping(valid_report_request, upstream_exception):
    mock_client = MagicMock()
    mock_client.generate_structured_json.side_effect = upstream_exception

    with pytest.raises(SleepReportServiceUpstreamError, match="failed to generate a valid report structure"):
        generate_sleep_report(
            request=valid_report_request,
            client_factory=lambda: mock_client,
        )


@pytest.mark.parametrize(
    "malformed_data",
    [
        {"summary": "Only summary provided"},  # Missing insights and recommendations
        {"summary": "Good", "insights": "Not a list", "recommendations": []},
        {"summary": 12345, "insights": [], "recommendations": []},
    ],
)
def test_malformed_gemini_output_schema_validation(valid_report_request, malformed_data):
    mock_client = MagicMock()
    mock_client.generate_structured_json.return_value = malformed_data

    with pytest.raises(SleepReportServiceUpstreamError, match="did not conform to the expected schema"):
        generate_sleep_report(
            request=valid_report_request,
            client_factory=lambda: mock_client,
        )