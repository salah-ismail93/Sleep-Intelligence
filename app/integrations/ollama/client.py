from typing import Any, Optional
import requests

from app.config.settings import OllamaSettings
from app.integrations.ollama.exceptions import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaModelNotFoundError,
    OllamaResponseParseError,
    OllamaTimeoutError,
)


class OllamaClient:
    """Isolated HTTP client adapter for interacting with Ollama chat API."""

    def __init__(
        self,
        settings: OllamaSettings,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.settings = settings
        self.session = session or requests.Session()

    def _build_url(self) -> str:
        base_url = self.settings.base_url.rstrip("/")
        return f"{base_url}/api/chat"

    def chat(self, messages: list[dict[str, Any]]) -> str:
        """Sends a list of message objects to Ollama /api/chat and returns content string."""
        url = self._build_url()
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "stream": False,
        }

        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.settings.timeout_seconds,
            )
        except requests.exceptions.Timeout as exc:
            raise OllamaTimeoutError("Ollama request timed out.") from exc
        except requests.exceptions.RequestException as exc:
            raise OllamaConnectionError("Failed to connect to Ollama service.") from exc

        if response.status_code == 404:
            raise OllamaModelNotFoundError(
                f"Model '{self.settings.model}' not found on Ollama server."
            )

        if not response.ok:
            raise OllamaHTTPError(status_code=response.status_code)

        try:
            data = response.json()
        except ValueError as exc:
            raise OllamaResponseParseError("Response body is not valid JSON.") from exc

        if not isinstance(data, dict):
            raise OllamaResponseParseError("Expected top-level JSON object in response.")

        message = data.get("message")
        if not isinstance(message, dict):
            raise OllamaResponseParseError("Missing or invalid 'message' object in response.")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise OllamaResponseParseError(
                "Response message 'content' is missing or empty."
            )

        return content