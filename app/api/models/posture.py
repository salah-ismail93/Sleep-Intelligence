from pydantic import BaseModel, Field, field_validator, model_validator
import math
from enum import Enum

class PostureLabel(str, Enum):
    SUPINE = "supine"
    PRONE = "prone"
    LEFT_SIDE = "left_side"
    RIGHT_SIDE = "right_side"
    UNKNOWN = "unknown"

class Quaternion(BaseModel):
    w: float
    x: float
    y: float
    z: float

    @field_validator("w", "x", "y", "z")
    @classmethod
    def validate_finite(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("Quaternion components must be finite real numbers.")
        return v

    @model_validator(mode="after")
    def validate_and_normalize(self) -> "Quaternion":
        norm = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if not (0.95 <= norm <= 1.05):
            raise ValueError(
                f"Quaternion norm ({norm:.4f}) must be within [0.95, 1.05]."
            )

        # Normalize to unit length
        self.w /= norm
        self.x /= norm
        self.y /= norm
        self.z /= norm
        return self
    
class PostureRequest(BaseModel):
    q_reference: Quaternion
    q_current: Quaternion
    
class PostureResponse(BaseModel):
    posture: PostureLabel
    confidence: float = Field(..., ge=0.0, le=1.0)