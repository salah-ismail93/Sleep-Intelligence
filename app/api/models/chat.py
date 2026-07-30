from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """User request model for sleep chat assistant."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message content for the sleep assistant.",
    )

    @field_validator("message")
    @classmethod
    def prevent_whitespace_only(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be empty or contain only whitespace.")
        return value


class ChatResponse(BaseModel):
    """Public response model from sleep chat assistant."""

    reply: str = Field(..., description="Assistant reply message content.")