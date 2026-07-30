from io import BytesIO
import wave

import numpy as np
import pytest

from app.algorithms.snore.detector import (
    FrameFeatures,
    classify_frame_features,
    detect_snore,
)


def create_wav_bytes(samples: np.ndarray, sample_rate: int = 8_000) -> bytes:
    pcm_samples = np.clip(samples * 32768.0, -32768, 32767).astype("<i2")
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_samples.tobytes())
    return buffer.getvalue()


def feature(
    *,
    rms: float = 0.02,
    centroid: float = 1_000.0,
    flatness: float = 0.01,
) -> FrameFeatures:
    return FrameFeatures(
        rms=rms,
        spectral_centroid_hz=centroid,
        spectral_flatness=flatness,
    )


def test_no_active_frames_returns_false_with_zero_confidence():
    frames = (feature(rms=0.0), feature(rms=0.009))

    result = classify_frame_features(frames)

    assert result.snore_detected is False
    assert result.confidence == 0.0


def test_confidence_uses_only_active_frames_as_denominator():
    frames = (
        feature(),
        feature(),
        feature(rms=0.0),
        feature(rms=0.02, centroid=200.0),
        feature(rms=0.0),
        feature(rms=0.02, centroid=200.0),
    )

    result = classify_frame_features(frames)

    assert result.confidence == pytest.approx(0.5)
    assert result.snore_detected is True


def test_fraction_threshold_alone_is_not_enough_without_consecutive_frames():
    frames = (
        feature(),
        feature(rms=0.02, centroid=200.0),
        feature(),
        feature(rms=0.02, centroid=200.0),
        feature(rms=0.02, centroid=200.0),
    )

    result = classify_frame_features(frames)

    assert result.confidence == pytest.approx(0.4)
    assert result.snore_detected is False


def test_two_consecutive_frames_at_fraction_boundary_are_detected():
    non_snore = feature(rms=0.02, centroid=200.0)
    frames = (feature(), feature()) + (non_snore,) * 8

    result = classify_frame_features(frames)

    assert result.confidence == pytest.approx(0.2)
    assert result.snore_detected is True


def test_spectral_flatness_threshold_rejects_noise_like_frames():
    frames = (
        feature(flatness=0.061),
        feature(flatness=0.061),
    )

    result = classify_frame_features(frames)

    assert result.snore_detected is False
    assert result.confidence == 0.0


def test_synthetic_high_frequency_tone_is_detected_end_to_end():
    sample_rate = 8_000
    time = np.arange(sample_rate, dtype=np.float64) / sample_rate
    samples = 0.1 * np.sin(2.0 * np.pi * 1_000.0 * time)

    result = detect_snore(create_wav_bytes(samples, sample_rate))

    assert result.snore_detected is True
    assert result.confidence == pytest.approx(1.0)


def test_synthetic_low_frequency_tone_is_not_detected_end_to_end():
    sample_rate = 8_000
    time = np.arange(sample_rate, dtype=np.float64) / sample_rate
    samples = 0.1 * np.sin(2.0 * np.pi * 200.0 * time)

    result = detect_snore(create_wav_bytes(samples, sample_rate))

    assert result.snore_detected is False
    assert result.confidence == 0.0


def test_silence_is_not_detected_end_to_end():
    samples = np.zeros(8_000, dtype=np.float64)

    result = detect_snore(create_wav_bytes(samples))

    assert result.snore_detected is False
    assert result.confidence == 0.0
