def compute_relative_quaternion(
    q_current: tuple[float, float, float, float],
    q_reference: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """Computes the relative rotation quaternion (q_current ⊗ q_reference⁻¹).

    Assumes both input quaternions are normalized unit quaternions in (w, x, y, z) order.

    Args:
        q_current: The current body orientation quaternion (w, x, y, z).
        q_reference: The reference/calibration orientation quaternion (w, x, y, z).

    Returns:
        tuple[float, float, float, float]: Relative quaternion (w, x, y, z).
    """
    w_curr, x_curr, y_curr, z_curr = q_current
    w_ref, x_ref, y_ref, z_ref = q_reference

    # Inverse of unit quaternion q_ref is its conjugate: (w, -x, -y, -z)
    w_inv = w_ref
    x_inv = -x_ref
    y_inv = -y_ref
    z_inv = -z_ref

    # Quaternion multiplication: q_current ⊗ q_reference⁻¹
    w = w_curr * w_inv - x_curr * x_inv - y_curr * y_inv - z_curr * z_inv
    x = w_curr * x_inv + x_curr * w_inv + y_curr * z_inv - z_curr * y_inv
    y = w_curr * y_inv - x_curr * z_inv + y_curr * w_inv + z_curr * x_inv
    z = w_curr * z_inv + x_curr * y_inv - y_curr * x_inv + z_curr * w_inv

    return w, x, y, z