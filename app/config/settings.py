from dataclasses import dataclass
import math
import os
from typing import Optional
from dotenv import dotenv_values


class SettingsError(ValueError):
    """Base exception for configuration and validation errors."""

    pass


@dataclass(frozen=True)
class OllamaSettings:
    """Immutable configuration settings for Ollama integration."""

    base_url: str
    model: str
    timeout_seconds: float

    def __post_init__(self) -> None:
        if not self.base_url or not self.base_url.strip():
            raise SettingsError("Ollama base URL cannot be blank.")

        if not self.model or not self.model.strip():
            raise SettingsError("Ollama model name cannot be blank.")

        if not math.isfinite(self.timeout_seconds):
            raise SettingsError(
                f"Ollama timeout must be a finite number, got {self.timeout_seconds}."
            )

        if self.timeout_seconds <= 0:
            raise SettingsError(
                f"Ollama timeout must be a positive number, got {self.timeout_seconds}."
            )


def get_ollama_settings(env_file_path: Optional[str] = ".env") -> OllamaSettings:
    """Loads Ollama settings from environment variables with fallback to .env file and defaults.

    Precedence order:
    1. Operating system environment variables.
    2. .env file variables (loaded via python-dotenv).
    3. Default values (matching .env.example).
    """
    file_env = dotenv_values(env_file_path) if env_file_path and os.path.exists(env_file_path) else {}

    def get_val(key: str, default: str) -> str:
        val = os.environ.get(key)
        if val is not None:
            return val
        file_val = file_env.get(key)
        if file_val is not None:
            return file_val
        return default

    base_url = get_val("OLLAMA_BASE_URL", "http://localhost:11434")
    model = get_val("OLLAMA_MODEL", "llama3.2:3b")
    raw_timeout = get_val("OLLAMA_TIMEOUT_SECONDS", "120")

    try:
        timeout_seconds = float(raw_timeout)
    except ValueError as exc:
        raise SettingsError(
            f"Invalid timeout value '{raw_timeout}': must be a valid number."
        ) from exc

    return OllamaSettings(
        base_url=base_url,
        model=model,
        timeout_seconds=timeout_seconds,
    )