import pytest

from app.config.settings import GeminiSettings, SettingsError, get_gemini_settings


def test_gemini_settings_defaults(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-secret-key-12345")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_TIMEOUT_SECONDS", raising=False)

    # Pass env_file_path=None to isolate from local .env files
    settings = get_gemini_settings(env_file_path=None)
    assert settings.api_key == "test-secret-key-12345"
    assert settings.model == "gemini-3.6-flash"
    assert settings.timeout_seconds == 120.0


def test_gemini_settings_custom_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "custom-key-999")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-pro")
    monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", "45.5")

    settings = get_gemini_settings(env_file_path=None)
    assert settings.api_key == "custom-key-999"
    assert settings.model == "gemini-3.5-pro"
    assert settings.timeout_seconds == 45.5


def test_env_file_loading_via_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_TIMEOUT_SECONDS", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        'GEMINI_API_KEY="file-api-key-abc"\n'
        "GEMINI_MODEL=gemini-1.5-pro\n"
        "GEMINI_TIMEOUT_SECONDS=60.0\n"
    )

    settings = get_gemini_settings(env_file_path=str(env_file))

    assert settings.api_key == "file-api-key-abc"
    assert settings.model == "gemini-1.5-pro"
    assert settings.timeout_seconds == 60.0


def test_environment_variable_overrides_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        'GEMINI_API_KEY="file-api-key-abc"\n'
        "GEMINI_MODEL=gemini-1.5-pro\n"
        "GEMINI_TIMEOUT_SECONDS=60.0\n"
    )

    # OS Environment variables take precedence over .env file
    monkeypatch.setenv("GEMINI_API_KEY", "os-override-api-key")
    monkeypatch.setenv("GEMINI_MODEL", "os-override-model")

    settings = get_gemini_settings(env_file_path=str(env_file))

    assert settings.api_key == "os-override-api-key"
    assert settings.model == "os-override-model"
    assert settings.timeout_seconds == 60.0  # Falls back to .env value when env var isn't set


@pytest.mark.parametrize("invalid_key", ["", "   ", "\t\n"])
def test_missing_or_blank_api_key(monkeypatch, invalid_key):
    monkeypatch.setenv("GEMINI_API_KEY", invalid_key)
    with pytest.raises(SettingsError, match="Gemini API key is required and cannot be blank."):
        get_gemini_settings(env_file_path=None)


@pytest.mark.parametrize("invalid_timeout", ["0", "-10", "abc", "inf", "nan"])
def test_invalid_timeout_seconds(monkeypatch, invalid_timeout):
    monkeypatch.setenv("GEMINI_API_KEY", "valid-key")
    monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", invalid_timeout)

    with pytest.raises(SettingsError):
        get_gemini_settings(env_file_path=None)


def test_secret_safe_representation():
    raw_secret = "super-secret-api-key-xyz789"
    settings = GeminiSettings(api_key=raw_secret, model="gemini-3.6-flash", timeout_seconds=60.0)

    repr_str = repr(settings)
    str_str = str(settings)

    assert raw_secret not in repr_str
    assert raw_secret not in str_str
    assert "***" in repr_str
    assert "gemini-3.6-flash" in repr_str