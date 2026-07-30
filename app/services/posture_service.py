from app.algorithms.posture.pipeline import classify_relative_quaternion
from app.algorithms.posture.quaternion import compute_relative_quaternion
from app.api.models.posture import PostureLabel, PostureRequest, PostureResponse


def classify_posture(request: PostureRequest) -> PostureResponse:
    """Classifies body posture based on current and reference quaternions.

    Args:
        request: PostureRequest containing normalized q_reference and q_current.

    Returns:
        PostureResponse with PostureLabel and confidence score.
    """
    q_curr_tuple = (
        request.q_current.w,
        request.q_current.x,
        request.q_current.y,
        request.q_current.z,
    )
    q_ref_tuple = (
        request.q_reference.w,
        request.q_reference.x,
        request.q_reference.y,
        request.q_reference.z,
    )

    # Compute relative quaternion q_rel = q_current ⊗ q_reference⁻¹
    q_rel = compute_relative_quaternion(q_curr_tuple, q_ref_tuple)

    # Classify relative orientation
    label_str, confidence = classify_relative_quaternion(*q_rel)

    return PostureResponse(
        posture=PostureLabel(label_str),
        confidence=confidence,
    )