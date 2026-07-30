from fastapi import APIRouter, HTTPException, status

from app.api.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import (
    ChatServiceTimeoutError,
    ChatServiceUnavailableError,
    ChatServiceUpstreamError,
    generate_chat_response,
)

router = APIRouter(prefix="/chat", tags=["Sleep Assistant Chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_with_assistant(request: ChatRequest) -> ChatResponse:
    try:
        return generate_chat_response(request.message)
    except ChatServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        )
    except ChatServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except ChatServiceUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )