from pydantic import BaseModel, Field


class SleepScoreRequest(BaseModel):
    total_sleep_minutes: float = Field(..., ge=0.0)
    sleep_efficiency: float = Field(..., ge=0.0, le=1.0)
    snore_event_count: int = Field(..., ge=0)
    posture_change_count: int = Field(..., ge=0)


class SleepScoreResponse(BaseModel):
    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description=(
            "Adult-oriented Version 1 wellness heuristic, clamped to [0.0, 100.0] "
            "and rounded to one decimal place. It is not a clinical or diagnostic score."
        ),
    )
