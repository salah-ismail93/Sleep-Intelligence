from app.api.models.chat import ChatRequest, ChatResponse


def generate_chat_reply(request: ChatRequest) -> ChatResponse:
    return ChatResponse(reply="Chat service placeholder response.")