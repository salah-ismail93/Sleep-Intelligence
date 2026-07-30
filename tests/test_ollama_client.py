import pytest
import requests

from app.config.settings import OllamaSettings
from app.integrations.ollama.client import OllamaClient
from app.integrations.ollama.exceptions import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaModelNotFoundError,
    OllamaResponseParseError,
    OllamaTimeoutError,
)


class MockResponse:
    def __init__(self, status_code: int = 200, json_data: dict = None, raw_text: str = None):
        self.status_code = status_code
        self._json_data = json_data
        self._raw_text = raw_text

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self):
        if self._raw_text is not None:
            raise ValueError("Invalid JSON")
        return self._json_data


@pytest.fixture
def default_settings():
    return OllamaSettings(
        base_url="http://localhost:11434",
        model="llama3.2:3b",
        timeout_seconds=120.0,
    )


def test_successful_chat_request_payload_and_parsing(default_settings, monkeypatch):
    messages = [{"role": "user", "content": "Hello"}]
    expected_content = "Hello! How can I help you today?"

    captured_args = {}

    def mock_post(url, json, timeout):
        captured_args["url"] = url
        captured_args["json"] = json
        captured_args["timeout"] = timeout
        return MockResponse(
            status_code=200,
            json_data={"message": {"role": "assistant", "content": expected_content}},
        )

    session = requests.Session()
    monkeypatch.setattr(session, "post", mock_post)

    client = OllamaClient(settings=default_settings, session=session)
    result = client.chat(messages)

    assert result == expected_content
    assert captured_args["url"] == "http://localhost:11434/api/chat"
    assert captured_args["json"] == {
        "model": "llama3.2:3b",
        "messages": messages,
        "stream": False,
    }
    assert captured_args["timeout"] == 120.0


def test_trailing_slash_base_url_handling(monkeypatch):
    settings = OllamaSettings(
        base_url="http://localhost:11434///",
        model="llama3.2:3b",
        timeout_seconds=30.0,
    )
    captured_url = None

    def mock_post(url, json, timeout):
        nonlocal captured_url
        captured_url = url
        return MockResponse(
            status_code=200,
            json_data={"message": {"content": "ok"}},
        )

    session = requests.Session()
    monkeypatch.setattr(session, "post", mock_post)

    client = OllamaClient(settings=settings, session=session)
    client.chat([{"role": "user", "content": "hi"}])

    assert captured_url == "http://localhost:11434/api/chat"


def test_timeout_exception(default_settings, monkeypatch):
    def mock_post(*args, **kwargs):
        raise requests.exceptions.Timeout("Request timed out")

    session = requests.Session()
    monkeypatch.setattr(session, "post", mock_post)

    client = OllamaClient(settings=default_settings, session=session)

    with pytest.raises(OllamaTimeoutError, match="Ollama request timed out."):
        client.chat([{"role": "user", "content": "test"}])


def test_connection_error_exception(default_settings, monkeypatch):
    def mock_post(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Connection refused")

    session = requests.Session()
    monkeypatch.setattr(session, "post", mock_post)

    client = OllamaClient(settings=default_settings, session=session)

    with pytest.raises(OllamaConnectionError, match="Failed to connect to Ollama service."):
        client.chat([{"role": "user", "content": "test"}])


def test_model_not_found_404(default_settings, monkeypatch):
    def mock_post(*args, **kwargs):
        return MockResponse(status_code=404, json_data={"error": "model 'llama3.2:3b' not found"})

    session = requests.Session()
    monkeypatch.setattr(session, "post", mock_post)

    client = OllamaClient(settings=default_settings, session=session)

    with pytest.raises(OllamaModelNotFoundError, match="Model 'llama3.2:3b' not found"):
        client.chat([{"role": "user", "content": "test"}])


def test_upstream_http_500_error(default_settings, monkeypatch):
    def mock_post(*args, **kwargs):
        return MockResponse(
            status_code=500,
            json_data={"error": "Internal Server Error Sensitive Body Data"},
        )

    session = requests.Session()
    monkeypatch.setattr(session, "post", mock_post)

    client = OllamaClient(settings=default_settings, session=session)

    with pytest.raises(OllamaHTTPError) as exc_info:
        client.chat([{"role": "user", "content": "test"}])

    assert exc_info.value.status_code == 500
    assert "Sensitive Body Data" not in str(exc_info.value)
    assert str(exc_info.value) == "Ollama returned HTTP error status 500."


def test_invalid_json_response(default_settings, monkeypatch):
    def mock_post(*args, **kwargs):
        return MockResponse(status_code=200, raw_text="Internal Server Error Page HTML")

    session = requests.Session()
    monkeypatch.setattr(session, "post", mock_post)

    client = OllamaClient(settings=default_settings, session=session)

    with pytest.raises(OllamaResponseParseError, match="Response body is not valid JSON."):
        client.chat([{"role": "user", "content": "test"}])


@pytest.mark.parametrize(
    "invalid_payload",
    [
        "not a dict",
        {},
        {"message": None},
        {"message": "not a dict"},
        {"message": {}},
        {"message": {"content": ""}},
        {"message": {"content": "   "}},
        {"message": {"content": 123}},
    ],
)
def test_invalid_or_missing_message_content(default_settings, monkeypatch, invalid_payload):
    def mock_post(*args, **kwargs):
        return MockResponse(status_code=200, json_data=invalid_payload)

    session = requests.Session()
    monkeypatch.setattr(session, "post", mock_post)

    client = OllamaClient(settings=default_settings, session=session)

    with pytest.raises(OllamaResponseParseError):
        client.chat([{"role": "user", "content": "test"}])