from app.algorithms.snore.wav_validation import (
    MalformedWAVError,
    UnsupportedWAVMediaTypeError,
    UnsupportedWAVPropertiesError,
    validate_and_extract_wav_metadata,
)
from app.api.models.snore import SnoreResponse


class SnoreServiceError(Exception):
    """Base exception for snore service operations."""

    pass


class SnoreUnsupportedMediaError(SnoreServiceError):
    """Raised when the uploaded file is not a supported WAV media container or encoding."""

    pass


class SnoreInvalidAudioError(SnoreServiceError):
    """Raised when the WAV audio is malformed, truncated, or has unsupported properties."""

    pass


def classify_snore(audio_bytes: bytes) -> SnoreResponse:
    """Validates snore audio bytes and returns snore analysis response schema."""
    try:
        validate_and_extract_wav_metadata(audio_bytes)
    except UnsupportedWAVMediaTypeError as exc:
        raise SnoreUnsupportedMediaError(str(exc)) from exc
    except (UnsupportedWAVPropertiesError, MalformedWAVError) as exc:
        raise SnoreInvalidAudioError(str(exc)) from exc

    return SnoreResponse(
        snore_detected=False,
        confidence=0.0,
    )