from fastapi import APIRouter, HTTPException, UploadFile, status

from app.api.models.snore import SnoreResponse
from app.services.snore_service import classify_snore

router = APIRouter()

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/snore", response_model=SnoreResponse)
async def compute_snore(audio: UploadFile) -> SnoreResponse:
    # Enforce .wav file extension
    if not audio.filename or not audio.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .wav audio files are supported.",
        )

    # Read at most MAX_AUDIO_SIZE_BYTES + 1 byte to catch oversized payloads without reading everything into memory
    content = await audio.read(MAX_AUDIO_SIZE_BYTES + 1)

    if len(content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File size exceeds maximum allowed limit of 10 MB.",
        )

    return classify_snore(content)