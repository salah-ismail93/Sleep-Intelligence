from typing import Callable, Optional

from app.config.settings import OllamaSettings, SettingsError, get_ollama_settings
from app.integrations.ollama.client import OllamaClient
from app.integrations.ollama.exceptions import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaIntegrationError,
    OllamaModelNotFoundError,
    OllamaResponseParseError,
    OllamaTimeoutError,
)
from app.api.models.chat import ChatResponse

SYSTEM_PROMPT = (
    "You are a helpful, empathetic sleep-education assistant. Provide evidence-based, general sleep hygiene "
    "and wellness advice. Do not provide medical diagnoses, treatment plans, or clinical assessments. "
    "Always advise users to consult a qualified healthcare professional for medical concerns or persistent sleep issues."
)


class ChatServiceError(Exception):
    """Base exception for chat service failures."""

    pass


class ChatServiceTimeoutError(ChatServiceError):
    """Raised when the upstream AI provider request times out."""

    pass


class ChatServiceUnavailableError(ChatServiceError):
    """Raised when the upstream AI service is unreachable or the requested model is missing."""

    pass


class ChatServiceUpstreamError(ChatServiceError):
    """Raised when upstream AI service returns bad responses or unexpected HTTP errors."""

    pass


def _default_client_factory() -> OllamaClient:
    """Default factory retrieving application settings and instantiating an OllamaClient."""
    settings: OllamaSettings = get_ollama_settings()
    return OllamaClient(settings=settings)


def generate_chat_response(
    user_message: str,
    client_factory: Optional[Callable[[], OllamaClient]] = None,
) -> ChatResponse:
    """Sends system and user messages to the Ollama integration and returns a ChatResponse."""
    factory = client_factory or _default_client_factory

    try:
        client = factory()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        reply_text = client.chat(messages)
    except SettingsError as exc:
        raise ChatServiceUnavailableError(
            "Upstream AI service is misconfigured."
        ) from exc
    except OllamaTimeoutError as exc:
        raise ChatServiceTimeoutError("Upstream AI request timed out.") from exc
    except (OllamaConnectionError, OllamaModelNotFoundError) as exc:
        raise ChatServiceUnavailableError(
            "Upstream AI service is currently unavailable or misconfigured."
        ) from exc
    except (OllamaHTTPError, OllamaResponseParseError, OllamaIntegrationError) as exc:
        raise ChatServiceUpstreamError(
            "Upstream AI service failed to generate a valid response."
        ) from exc

    return ChatResponse(reply=reply_text)