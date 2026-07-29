from fastapi.testclient import TestClient
from app.api.models.posture import Quaternion
import math
import pytest
from pydantic import ValidationError

from app.main import app

client = TestClient(app)


def test_posture_endpoint_returns_placeholder_response():
    payload = {
        "q_reference": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        "q_current": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "posture": "unknown",
        "confidence": 0.0,
    }
    
    
def test_slightly_non_unit_quaternion_is_accepted_and_normalized():
    # Magnitude = sqrt(1.02^2) = 1.02, within [0.95, 1.05]
    q = Quaternion(w=1.02, x=0.0, y=0.0, z=0.0)
    
    # Verify component normalization to unit length
    assert math.isclose(q.w, 1.0)
    assert q.x == 0.0
    assert q.y == 0.0
    assert q.z == 0.0


def test_zero_quaternion_is_rejected():
    with pytest.raises(ValidationError):
        Quaternion(w=0.0, x=0.0, y=0.0, z=0.0)


def test_out_of_range_quaternion_returns_422():
    payload = {
        "q_reference": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        # Norm = sqrt(2^2) = 2.0 (outside [0.95, 1.05])
        "q_current": {"w": 2.0, "x": 0.0, "y": 0.0, "z": 0.0},
    }

    response = client.post("/posture", json=payload)

    assert response.status_code == 422