from app.api.models.snore import SnoreResponse


def classify_snore(audio_bytes: bytes) -> SnoreResponse:
    return SnoreResponse(
        snore_detected=False,
        confidence=0.0,
    )