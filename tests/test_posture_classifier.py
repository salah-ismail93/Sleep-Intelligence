import math
import pytest

from app.algorithms.posture.classifier import classify_gravity_vector


# --- Supported Posture Examples ---

def test_classify_supine_clear_example():
    label, confidence = classify_gravity_vector(gx=0.0, gy=0.0, gz=0.98)
    assert label == "supine"
    assert math.isclose(confidence, 0.98)


def test_classify_prone_clear_example():
    label, confidence = classify_gravity_vector(gx=0.0, gy=0.0, gz=-0.95)
    assert label == "prone"
    assert math.isclose(confidence, 0.95)


def test_classify_left_side_clear_example():
    label, confidence = classify_gravity_vector(gx=-0.85, gy=0.0, gz=0.0)
    assert label == "left_side"
    assert math.isclose(confidence, 0.85)


def test_classify_right_side_clear_example():
    label, confidence = classify_gravity_vector(gx=0.88, gy=0.0, gz=0.0)
    assert label == "right_side"
    assert math.isclose(confidence, 0.88)


# --- Ambiguous / Unknown Example ---

def test_classify_ambiguous_unknown_example():
    # Neither gx nor gz dominates
    label, confidence = classify_gravity_vector(gx=0.50, gy=0.50, gz=0.50)
    assert label == "unknown"
    # confidence = 1.0 - max(|0.50|, |0.50|) = 0.50
    assert math.isclose(confidence, 0.50)


# --- Exact Threshold Boundaries ---

def test_exact_threshold_supine_boundary():
    label, confidence = classify_gravity_vector(gx=0.0, gy=0.0, gz=0.80)
    assert label == "supine"
    assert math.isclose(confidence, 0.80)


def test_exact_threshold_prone_boundary():
    label, confidence = classify_gravity_vector(gx=0.0, gy=0.0, gz=-0.90)
    assert label == "prone"
    assert math.isclose(confidence, 0.90)


def test_exact_threshold_left_side_boundary():
    label, confidence = classify_gravity_vector(gx=-0.80, gy=0.0, gz=0.0)
    assert label == "left_side"
    assert math.isclose(confidence, 0.80)


def test_exact_threshold_right_side_boundary():
    label, confidence = classify_gravity_vector(gx=0.80, gy=0.0, gz=0.0)
    assert label == "right_side"
    assert math.isclose(confidence, 0.80)


def test_just_below_supine_boundary_returns_unknown():
    label, confidence = classify_gravity_vector(gx=0.0, gy=0.0, gz=0.799)
    assert label == "unknown"
    assert math.isclose(confidence, 1.0 - 0.799)


# --- Confidence Values and [0, 1] Bounds ---

@pytest.mark.parametrize(
    "gx,gy,gz",
    [
        (0.0, 0.0, 1.0),
        (0.0, 0.0, -1.0),
        (-1.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
        (0.6, 0.6, 0.6),
        (-0.79, 0.0, -0.89),
    ],
)
def test_confidence_always_within_zero_to_one_bounds(gx: float, gy: float, gz: float):
    _, confidence = classify_gravity_vector(gx, gy, gz)
    assert 0.0 <= confidence <= 1.0