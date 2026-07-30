from app.algorithms.snore.detector import SnoreDetection, detect_snore
from app.algorithms.snore.wav_validation import (
    MalformedWAVError,
    UnsupportedWAVMediaTypeError,
    UnsupportedWAVPropertiesError,
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
    """Delegates audio parsing, validation, and feature detection to detect_snore,

    translating algorithm-level errors into service-level exceptions.
    """
    try:
        detection: SnoreDetection = detect_snore(audio_bytes)
    except UnsupportedWAVMediaTypeError as exc:
        raise SnoreUnsupportedMediaError(str(exc)) from exc
    except (UnsupportedWAVPropertiesError, MalformedWAVError) as exc:
        raise SnoreInvalidAudioError(str(exc)) from exc

    return SnoreResponse(
        snore_detected=detection.snore_detected,
        confidence=detection.confidence,
    )