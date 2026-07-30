import sys
from unittest.mock import MagicMock
import pytest

from app.config.settings import GeminiSettings
from app.integrations.gemini.client import GeminiClient
from app.integrations.gemini.exceptions import (
    GeminiAuthenticationError,
    GeminiConnectionError,
    GeminiIntegrationError,
    GeminiRateLimitError,
    GeminiResponseParseError,
    GeminiTimeoutError,
)


@pytest.fixture
def gemini_settings():
    return GeminiSettings(
        api_key="secret-api-key-12345",
        model="gemini-3.6-flash",
        timeout_seconds=60.0,
    )


class MockGenerateContentResponse:
    def __init__(self, text: str):
        self.text = text


def test_real_client_constructor_parameters(monkeypatch, gemini_settings):
    mock_genai_module = MagicMock()
    mock_http_options_cls = MagicMock()
    mock_genai_module.types.HttpOptions = mock_http_options_cls

    monkeypatch.setitem(sys.modules, "google.genai", mock_genai_module)
    monkeypatch.setitem(sys.modules, "google.genai.types", mock_genai_module.types)

    GeminiClient(settings=gemini_settings)

    # Verify 60.0 seconds became 60000 milliseconds
    mock_http_options_cls.assert_called_once_with(timeout=60000)
    mock_genai_module.Client.assert_called_once_with(
        api_key="secret-api-key-12345",
        http_options=mock_http_options_cls.return_value,
    )


def test_successful_structured_json_generation(gemini_settings):
    mock_sdk = MagicMock()
    expected_dict = {"quality_score": 85, "recommendations": ["Maintain consistent sleep schedule."]}
    mock_sdk.models.generate_content.return_value = MockGenerateContentResponse(
        text='{"quality_score": 85, "recommendations": ["Maintain consistent sleep schedule."]}'
    )

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)
    result = client.generate_structured_json(prompt="Analyze sleep data")

    assert result == expected_dict
    mock_sdk.models.generate_content.assert_called_once_with(
        model="gemini-3.6-flash",
        contents="Analyze sleep data",
        config={"response_mime_type": "application/json"},
    )


def test_successful_generation_with_schema(gemini_settings):
    mock_sdk = MagicMock()
    mock_sdk.models.generate_content.return_value = MockGenerateContentResponse(
        text='{"score": 90}'
    )

    schema = {"type": "object", "properties": {"score": {"type": "integer"}}}

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)
    result = client.generate_structured_json(prompt="Analyze", response_schema=schema)

    assert result == {"score": 90}
    mock_sdk.models.generate_content.assert_called_once_with(
        model="gemini-3.6-flash",
        contents="Analyze",
        config={
            "response_mime_type": "application/json",
            "response_schema": schema,
        },
    )


def test_timeout_exception(gemini_settings):
    mock_sdk = MagicMock()
    mock_sdk.models.generate_content.side_effect = Exception("Request deadline exceeded timed out")

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)

    with pytest.raises(GeminiTimeoutError, match="Gemini request timed out."):
        client.generate_structured_json("Prompt")


def test_authentication_error_exception(gemini_settings):
    mock_sdk = MagicMock()
    mock_sdk.models.generate_content.side_effect = Exception("401 Unauthorized: Invalid API key")

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)

    with pytest.raises(GeminiAuthenticationError, match="Gemini authentication failed."):
        client.generate_structured_json("Prompt")


def test_rate_limit_exception(gemini_settings):
    mock_sdk = MagicMock()
    mock_sdk.models.generate_content.side_effect = Exception("429 ResourceExhausted: Quota exceeded")

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)

    with pytest.raises(GeminiRateLimitError, match="Gemini rate limit or quota exceeded."):
        client.generate_structured_json("Prompt")


def test_connection_error_exception(gemini_settings):
    mock_sdk = MagicMock()
    mock_sdk.models.generate_content.side_effect = Exception("503 Service Unavailable: Network error")

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)

    with pytest.raises(GeminiConnectionError, match="Failed to communicate with Gemini service."):
        client.generate_structured_json("Prompt")


def test_generic_upstream_exception(gemini_settings):
    mock_sdk = MagicMock()
    mock_sdk.models.generate_content.side_effect = Exception("Unexpected server glitch")

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)

    with pytest.raises(GeminiIntegrationError, match="Gemini request failed due to an upstream error."):
        client.generate_structured_json("Prompt")


def test_secret_is_never_leaked_in_exception(gemini_settings):
    mock_sdk = MagicMock()
    mock_sdk.models.generate_content.side_effect = Exception(
        f"Error using key {gemini_settings.api_key}"
    )

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)

    with pytest.raises(GeminiIntegrationError) as exc_info:
        client.generate_structured_json("Prompt")

    assert gemini_settings.api_key not in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_response",
    [
        MockGenerateContentResponse(text=""),
        MockGenerateContentResponse(text="   "),
        MockGenerateContentResponse(text="Not JSON content"),
        MockGenerateContentResponse(text='["item1", "item2"]'),
        None,
    ],
)
def test_invalid_or_empty_response(gemini_settings, invalid_response):
    mock_sdk = MagicMock()
    mock_sdk.models.generate_content.return_value = invalid_response

    client = GeminiClient(settings=gemini_settings, client=mock_sdk)

    with pytest.raises(GeminiResponseParseError):
        client.generate_structured_json("Prompt")