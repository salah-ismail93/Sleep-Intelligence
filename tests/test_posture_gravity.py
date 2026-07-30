import math

import pytest

from app.algorithms.posture.gravity import quaternion_to_gravity


def test_identity_quaternion_maps_gravity_to_positive_z():
    gravity = quaternion_to_gravity(w=1.0, x=0.0, y=0.0, z=0.0)

    assert gravity == pytest.approx((0.0, 0.0, 1.0))


def test_positive_90_degree_y_rotation_maps_gravity_to_negative_x():
    half_angle = math.pi / 4.0

    gravity = quaternion_to_gravity(
        w=math.cos(half_angle),
        x=0.0,
        y=math.sin(half_angle),
        z=0.0,
    )

    assert gravity == pytest.approx((-1.0, 0.0, 0.0), abs=1e-12)


def test_180_degree_y_rotation_maps_gravity_to_negative_z():
    gravity = quaternion_to_gravity(w=0.0, x=0.0, y=1.0, z=0.0)

    assert gravity == pytest.approx((0.0, 0.0, -1.0), abs=1e-12)
