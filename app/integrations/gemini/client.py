import json
from typing import Any, Optional

from app.config.settings import GeminiSettings
from app.integrations.gemini.exceptions import (
    GeminiAuthenticationError,
    GeminiConnectionError,
    GeminiIntegrationError,
    GeminiRateLimitError,
    GeminiResponseParseError,
    GeminiTimeoutError,
)


class GeminiClient:
    """Isolated client adapter for requesting structured JSON generation from Gemini."""

    def __init__(
        self,
        settings: GeminiSettings,
        client: Optional[Any] = None,
    ) -> None:
        self.settings = settings
        if client is not None:
            self._client = client
        else:
            try:
                from google import genai
                from google.genai.types import HttpOptions
            except ImportError as exc:
                raise GeminiIntegrationError(
                    "google-genai library is required but not installed."
                ) from exc

            timeout_ms = int(settings.timeout_seconds * 1000)
            self._client = genai.Client(
                api_key=settings.api_key,
                http_options=HttpOptions(timeout=timeout_ms),
            )

    def generate_structured_json(
        self,
        prompt: str,
        response_schema: Optional[Any] = None,
    ) -> dict[str, Any]:
        """Sends a prompt to Gemini requesting JSON output and returns a parsed dictionary."""
        config: dict[str, Any] = {
            "response_mime_type": "application/json",
        }
        if response_schema is not None:
            config["response_schema"] = response_schema

        try:
            response = self._client.models.generate_content(
                model=self.settings.model,
                contents=prompt,
                config=config,
            )
        except Exception as exc:
            self._handle_exception(exc)

        if not response or not hasattr(response, "text"):
            raise GeminiResponseParseError("Gemini response is empty or missing content.")

        raw_text = response.text
        if not raw_text or not raw_text.strip():
            raise GeminiResponseParseError("Gemini response content is blank.")

        try:
            data = json.loads(raw_text)
        except (ValueError, TypeError) as exc:
            raise GeminiResponseParseError("Gemini response body is not valid JSON.") from exc

        if not isinstance(data, dict):
            raise GeminiResponseParseError(
                f"Expected JSON object (dict) from Gemini response, got {type(data).__name__}."
            )

        return data

    def _handle_exception(self, exc: Exception) -> None:
        """Categorizes SDK or HTTP exceptions into Gemini integration exceptions without exposing API key."""
        exc_str = str(exc).lower()

        # Secret sanitization guard
        if self.settings.api_key and self.settings.api_key in str(exc):
            raise GeminiIntegrationError("Gemini integration request failed.") from None

        if "timeout" in exc_str or "timed out" in exc_str or "deadline" in exc_str:
            raise GeminiTimeoutError("Gemini request timed out.") from exc

        if (
            "401" in exc_str
            or "403" in exc_str
            or "unauthorized" in exc_str
            or "forbidden" in exc_str
            or "invalid api key" in exc_str
            or "unauthenticated" in exc_str
        ):
            raise GeminiAuthenticationError("Gemini authentication failed.") from exc

        if "429" in exc_str or "resource_exhausted" in exc_str or "quota" in exc_str or "rate limit" in exc_str:
            raise GeminiRateLimitError("Gemini rate limit or quota exceeded.") from exc

        if (
            "connection" in exc_str
            or "unavailable" in exc_str
            or "503" in exc_str
            or "504" in exc_str
            or "network" in exc_str
        ):
            raise GeminiConnectionError("Failed to communicate with Gemini service.") from exc

        raise GeminiIntegrationError("Gemini request failed due to an upstream error.") from exc