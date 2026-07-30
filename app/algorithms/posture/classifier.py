def classify_gravity_vector(
    gx: float, gy: float, gz: float
) -> tuple[str, float]:
    """Classifies body posture and calculates alignment confidence statelessly.

    Args:
        gx: Gravity vector X component.
        gy: Gravity vector Y component.
        gz: Gravity vector Z component.

    Returns:
        tuple[str, float]: (posture_label_string, confidence_score)
    """
    # 1. Supine: gz >= 0.80
    if gz >= 0.80:
        confidence = abs(gz)
        return "supine", min(1.0, max(0.0, float(confidence)))

    # 2. Prone: gz <= -0.90
    if gz <= -0.90:
        confidence = abs(gz)
        return "prone", min(1.0, max(0.0, float(confidence)))

    # 3. Left Side: gx <= -0.80
    if gx <= -0.80:
        confidence = abs(gx)
        return "left_side", min(1.0, max(0.0, float(confidence)))

    # 4. Right Side: gx >= 0.80
    if gx >= 0.80:
        confidence = abs(gx)
        return "right_side", min(1.0, max(0.0, float(confidence)))

    # 5. Unknown: Otherwise
    confidence = 1.0 - max(abs(gx), abs(gz))
    return "unknown", min(1.0, max(0.0, float(confidence)))