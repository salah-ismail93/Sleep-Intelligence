from app.api.models.posture import PostureLabel, PostureRequest, PostureResponse


def classify_posture(request: PostureRequest) -> PostureResponse:
    return PostureResponse(
        posture=PostureLabel.UNKNOWN,
        confidence=0.0,
    )