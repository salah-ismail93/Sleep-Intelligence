import math
from app.algorithms.posture.pipeline import classify_relative_quaternion


def test_identity_quaternion_returns_supine():
    # Identity quaternion: q = (1, 0, 0, 0) -> gx=0, gy=0, gz=1
    label, confidence = classify_relative_quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    assert label == "supine"
    assert math.isclose(confidence, 1.0)


def test_180_deg_y_rotation_quaternion_returns_prone():
    # 180° rotation around Y-axis: q = (0, 0, 1, 0) -> gx=0, gy=0, gz=-1
    label, confidence = classify_relative_quaternion(w=0.0, x=0.0, y=1.0, z=0.0)
    assert label == "prone"
    assert math.isclose(confidence, 1.0)


def test_plus_90_deg_y_rotation_quaternion_returns_left_side():
    # +90° rotation around Y-axis: q = (cos(45°), 0, sin(45°), 0) -> gx=-1, gy=0, gz=0
    w = math.cos(math.pi / 4)
    y = math.sin(math.pi / 4)
    label, confidence = classify_relative_quaternion(w=w, x=0.0, y=y, z=0.0)
    assert label == "left_side"
    assert math.isclose(confidence, 1.0, abs_tol=1e-7)


def test_minus_90_deg_y_rotation_quaternion_returns_right_side():
    # -90° rotation around Y-axis: q = (cos(-45°), 0, sin(-45°), 0) -> gx=1, gy=0, gz=0
    w = math.cos(-math.pi / 4)
    y = math.sin(-math.pi / 4)
    label, confidence = classify_relative_quaternion(w=w, x=0.0, y=y, z=0.0)
    assert label == "right_side"
    assert math.isclose(confidence, 1.0, abs_tol=1e-7)


def test_ambiguous_orientation_quaternion_returns_unknown():
    # Ambiguous tilt giving gx=0.5, gy=0.5, gz=0.707 (gz < 0.80 and gx < 0.80)
    label, confidence = classify_relative_quaternion(
        w=0.85355339, x=0.35355339, y=0.35355339, z=0.14644661
    )
    assert label == "unknown"
    assert 0.0 <= confidence <= 1.0