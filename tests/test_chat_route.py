from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.config.settings import SettingsError
from app.integrations.ollama.exceptions import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaModelNotFoundError,
    OllamaResponseParseError,
    OllamaTimeoutError,
)
from app.main import app
from app.services.chat_service import SYSTEM_PROMPT

client = TestClient(app)


def test_chat_successful_response(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.return_value = "Consistent sleep schedules improve circadian rhythm stability."

    monkeypatch.setattr(
        "app.services.chat_service._default_client_factory",
        lambda: mock_client,
    )

    response = client.post("/chat", json={"message": "How can I improve my sleep structure?"})

    assert response.status_code == 200
    assert response.json() == {
        "reply": "Consistent sleep schedules improve circadian rhythm stability."
    }

    mock_client.chat.assert_called_once_with([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "How can I improve my sleep structure?"},
    ])


def test_chat_timeout_mapping_504(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.side_effect = OllamaTimeoutError("Timed out")
    monkeypatch.setattr("app.services.chat_service._default_client_factory", lambda: mock_client)

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 504
    assert "timed out" in response.json()["detail"].lower()


@pytest.mark.parametrize(
    "factory_side_effect",
    [
        OllamaConnectionError("Connection refused"),
        OllamaModelNotFoundError("Model missing"),
    ],
)
def test_chat_unavailable_mapping_503(monkeypatch, factory_side_effect):
    mock_client = MagicMock()
    mock_client.chat.side_effect = factory_side_effect
    monkeypatch.setattr("app.services.chat_service._default_client_factory", lambda: mock_client)

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_chat_configuration_failure_mapping_503(monkeypatch):
    def failing_factory():
        raise SettingsError("Ollama base URL cannot be blank.")

    monkeypatch.setattr("app.services.chat_service._default_client_factory", failing_factory)

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 503
    assert "misconfigured" in response.json()["detail"].lower()


@pytest.mark.parametrize(
    "adapter_exception",
    [
        OllamaHTTPError(500),
        OllamaResponseParseError("Bad JSON"),
    ],
)
def test_chat_upstream_error_mapping_502(monkeypatch, adapter_exception):
    mock_client = MagicMock()
    mock_client.chat.side_effect = adapter_exception
    monkeypatch.setattr("app.services.chat_service._default_client_factory", lambda: mock_client)

    response = client.post("/chat", json={"message": "Hello"})

    assert response.status_code == 502
    assert "failed" in response.json()["detail"].lower()


# Endpoint input validation boundary tests (422 response status)
def test_chat_empty_message_returns_422():
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_whitespace_only_message_returns_422():
    response = client.post("/chat", json={"message": "    "})
    assert response.status_code == 422


def test_chat_exceeds_max_length_returns_422():
    response = client.post("/chat", json={"message": "a" * 2001})
    assert response.status_code == 422