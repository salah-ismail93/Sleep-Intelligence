import math
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# --- Classification Integration Tests ---

def test_identical_current_and_reference_returns_supine():
    payload = {
        "q_reference": {"w": 0.70710678, "x": 0.0, "y": 0.70710678, "z": 0.0},
        "q_current": {"w": 0.70710678, "x": 0.0, "y": 0.70710678, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["posture"] == "supine"
    assert math.isclose(data["confidence"], 1.0, abs_tol=1e-5)


def test_identity_reference_with_180_deg_y_current_returns_prone():
    # 180° Y rotation: q = (0, 0, 1, 0)
    payload = {
        "q_reference": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        "q_current": {"w": 0.0, "x": 0.0, "y": 1.0, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["posture"] == "prone"
    assert math.isclose(data["confidence"], 1.0, abs_tol=1e-5)


def test_identity_reference_with_plus_90_deg_y_current_returns_left_side():
    # +90° Y rotation: q = (cos(45°), 0, sin(45°), 0)
    w = math.cos(math.pi / 4)
    y = math.sin(math.pi / 4)
    payload = {
        "q_reference": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        "q_current": {"w": w, "x": 0.0, "y": y, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["posture"] == "left_side"
    assert math.isclose(data["confidence"], 1.0, abs_tol=1e-5)


def test_identity_reference_with_minus_90_deg_y_current_returns_right_side():
    # -90° Y rotation: q = (cos(-45°), 0, sin(-45°), 0)
    w = math.cos(-math.pi / 4)
    y = math.sin(-math.pi / 4)
    payload = {
        "q_reference": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        "q_current": {"w": w, "x": 0.0, "y": y, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["posture"] == "right_side"
    assert math.isclose(data["confidence"], 1.0, abs_tol=1e-5)


def test_ambiguous_valid_orientation_returns_unknown():
    # Tilt producing intermediate gx and gz values below thresholds
    payload = {
        "q_reference": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        "q_current": {
            "w": 0.85355339,
            "x": 0.35355339,
            "y": 0.35355339,
            "z": 0.14644661,
        },
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["posture"] == "unknown"
    assert 0.0 <= data["confidence"] <= 1.0


# --- Restored API Validation Edge-Case Tests ---

def test_slightly_non_unit_quaternion_is_accepted_and_normalized():
    # Norm = 1.01 (within [0.95, 1.05] range)
    payload = {
        "q_reference": {"w": 1.01, "x": 0.0, "y": 0.0, "z": 0.0},
        "q_current": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 200
    assert response.json()["posture"] == "supine"


def test_zero_quaternion_returns_422():
    # Norm = 0.0 (outside [0.95, 1.05] range)
    payload = {
        "q_reference": {"w": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
        "q_current": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 422


def test_out_of_range_quaternion_returns_422():
    # Norm = 2.0 (outside [0.95, 1.05] range)
    payload = {
        "q_reference": {"w": 2.0, "x": 0.0, "y": 0.0, "z": 0.0},
        "q_current": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 422