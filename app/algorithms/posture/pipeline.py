from app.algorithms.posture.classifier import classify_gravity_vector
from app.algorithms.posture.gravity import quaternion_to_gravity


def classify_relative_quaternion(
    w: float, x: float, y: float, z: float
) -> tuple[str, float]:
    """Orchestrates posture classification for a normalized relative quaternion.

    Args:
        w: Quaternion scalar component.
        x: Quaternion X component.
        y: Quaternion Y component.
        z: Quaternion Z component.

    Returns:
        tuple[str, float]: (posture_label_string, confidence_score)
    """
    gx, gy, gz = quaternion_to_gravity(w, x, y, z)
    return classify_gravity_vector(gx, gy, gz)