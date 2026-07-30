import math
import pytest

from app.config.settings import OllamaSettings, SettingsError, get_ollama_settings


def test_default_ollama_settings_matches_env_example(monkeypatch, tmp_path):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_TIMEOUT_SECONDS", raising=False)

    non_existent_env = str(tmp_path / ".env.nonexistent")
    settings = get_ollama_settings(env_file_path=non_existent_env)

    assert settings.base_url == "http://localhost:11434"
    assert settings.model == "llama3.2:3b"
    assert settings.timeout_seconds == 120.0


def test_environment_variable_overrides(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama-service:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "mistral:latest")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "60.0")

    settings = get_ollama_settings(env_file_path=None)

    assert settings.base_url == "http://ollama-service:11434"
    assert settings.model == "mistral:latest"
    assert settings.timeout_seconds == 60.0


def test_env_file_loading_via_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_TIMEOUT_SECONDS", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        'OLLAMA_BASE_URL="http://custom-host:11434"\n'
        'OLLAMA_MODEL=qwen2.5:7b\n'
        "OLLAMA_TIMEOUT_SECONDS=45\n"
    )

    settings = get_ollama_settings(env_file_path=str(env_file))

    assert settings.base_url == "http://custom-host:11434"
    assert settings.model == "qwen2.5:7b"
    assert settings.timeout_seconds == 45.0


@pytest.mark.parametrize(
    "base_url, model, timeout_seconds, expected_msg",
    [
        ("", "llama3.2:3b", 120.0, "Ollama base URL cannot be blank."),
        ("   ", "llama3.2:3b", 120.0, "Ollama base URL cannot be blank."),
        ("http://localhost:11434", "", 120.0, "Ollama model name cannot be blank."),
        ("http://localhost:11434", "  ", 120.0, "Ollama model name cannot be blank."),
        ("http://localhost:11434", "llama3.2:3b", 0.0, "Ollama timeout must be a positive number"),
        ("http://localhost:11434", "llama3.2:3b", -10.0, "Ollama timeout must be a positive number"),
        ("http://localhost:11434", "llama3.2:3b", float("nan"), "Ollama timeout must be a finite number"),
        ("http://localhost:11434", "llama3.2:3b", float("inf"), "Ollama timeout must be a finite number"),
        ("http://localhost:11434", "llama3.2:3b", float("-inf"), "Ollama timeout must be a finite number"),
    ],
)
def test_invalid_settings_validation(base_url, model, timeout_seconds, expected_msg):
    with pytest.raises(SettingsError, match=expected_msg):
        OllamaSettings(base_url=base_url, model=model, timeout_seconds=timeout_seconds)


def test_non_finite_timeout_strings_via_loader(monkeypatch):
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "inf")

    with pytest.raises(SettingsError, match="Ollama timeout must be a finite number"):
        get_ollama_settings(env_file_path=None)


def test_invalid_timeout_string_conversion(monkeypatch):
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "not-a-number")

    with pytest.raises(SettingsError, match="Invalid timeout value 'not-a-number'"):
        get_ollama_settings(env_file_path=None)


def test_settings_immutability():
    settings = OllamaSettings(base_url="http://localhost:11434", model="llama3.2:3b", timeout_seconds=120.0)

    with pytest.raises(AttributeError):
        settings.timeout_seconds = 45.0