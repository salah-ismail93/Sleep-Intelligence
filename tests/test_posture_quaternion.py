import math
from app.algorithms.posture.quaternion import compute_relative_quaternion


def test_identity_reference_returns_current_quaternion():
    q_current = (0.70710678, 0.0, 0.70710678, 0.0)
    q_reference = (1.0, 0.0, 0.0, 0.0)

    result = compute_relative_quaternion(q_current, q_reference)

    for res, expected in zip(result, q_current):
        assert math.isclose(res, expected, abs_tol=1e-7)


def test_identical_current_and_reference_produce_identity_rotation():
    q_current = (0.6, 0.8, 0.0, 0.0)
    q_reference = (0.6, 0.8, 0.0, 0.0)

    w, x, y, z = compute_relative_quaternion(q_current, q_reference)

    assert math.isclose(w, 1.0, abs_tol=1e-7)
    assert math.isclose(x, 0.0, abs_tol=1e-7)
    assert math.isclose(y, 0.0, abs_tol=1e-7)
    assert math.isclose(z, 0.0, abs_tol=1e-7)


def test_known_reference_current_pair_produces_expected_relative_rotation():
    # Reference: +45° pitch around Y-axis -> (cos(22.5°), 0, sin(22.5°), 0)
    q_reference = (math.cos(math.pi / 8), 0.0, math.sin(math.pi / 8), 0.0)

    # Current: +90° pitch around Y-axis -> (cos(45°), 0, sin(45°), 0)
    q_current = (math.cos(math.pi / 4), 0.0, math.sin(math.pi / 4), 0.0)

    # Expected relative rotation: (90° - 45°) = +45° pitch around Y-axis
    q_expected = (math.cos(math.pi / 8), 0.0, math.sin(math.pi / 8), 0.0)

    result = compute_relative_quaternion(q_current, q_reference)

    for res, exp in zip(result, q_expected):
        assert math.isclose(res, exp, abs_tol=1e-7)


def test_inputs_are_not_mutated():
    q_current = (0.70710678, 0.0, 0.70710678, 0.0)
    q_reference = (0.6, 0.8, 0.0, 0.0)

    q_current_copy = tuple(q_current)
    q_reference_copy = tuple(q_reference)

    _ = compute_relative_quaternion(q_current, q_reference)

    assert q_current == q_current_copy
    assert q_reference == q_reference_copy