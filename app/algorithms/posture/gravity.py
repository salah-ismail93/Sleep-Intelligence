def quaternion_to_gravity(
    w: float,
    x: float,
    y: float,
    z: float,
) -> tuple[float, float, float]:
    """Return the device-frame gravity vector for a unit quaternion."""
    gx = 2.0 * (x * z - w * y)
    gy = 2.0 * (w * x + y * z)
    gz = w * w - x * x - y * y + z * z

    return gx, gy, gz
