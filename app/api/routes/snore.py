from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.models.snore import SnoreResponse
from app.services.snore_service import (
    SnoreInvalidAudioError,
    SnoreUnsupportedMediaError,
    classify_snore,
)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MiB

router = APIRouter(prefix="/snore", tags=["Snore Analysis"])


@router.post("", response_model=SnoreResponse, status_code=status.HTTP_200_OK)
async def analyze_snore(audio: UploadFile = File(...)) -> SnoreResponse:
    if not audio.filename or not audio.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file format. Only .wav files are allowed.",
        )

    content = await audio.read(MAX_FILE_SIZE_BYTES + 1)
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File size exceeds the 10 MiB limit.",
        )

    try:
        return classify_snore(content)
    except SnoreUnsupportedMediaError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        )
    except SnoreInvalidAudioError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )