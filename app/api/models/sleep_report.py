from typing import List
from pydantic import BaseModel, Field


class SleepReportRequest(BaseModel):
    total_sleep_minutes: float = Field(..., ge=0.0)
    sleep_efficiency: float = Field(..., ge=0.0, le=1.0)
    sleep_score: float = Field(..., ge=0.0, le=100.0)
    snore_event_count: int = Field(..., ge=0)
    posture_change_count: int = Field(..., ge=0)


class SleepReportResponse(BaseModel):
    summary: str
    insights: List[str]
    recommendations: List[str]