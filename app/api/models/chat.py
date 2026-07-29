from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)

    @field_validator("message")
    @classmethod
    def validate_not_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace-only.")
        return v


class ChatResponse(BaseModel):
    reply: str