from pydantic import BaseModel, Field


class SnoreResponse(BaseModel):
    """Public snore detection analysis response schema."""

    snore_detected: bool = Field(..., description="Whether a snore event was detected.")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Detection confidence score between 0.0 and 1.0."
    )