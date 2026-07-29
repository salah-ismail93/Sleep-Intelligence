from fastapi import APIRouter

from app.api.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_chat_reply

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest) -> ChatResponse:
    return generate_chat_reply(request)