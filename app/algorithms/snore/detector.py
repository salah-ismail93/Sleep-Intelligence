from dataclasses import dataclass
from io import BytesIO
import wave

import numpy as np
from numpy.typing import NDArray

from app.algorithms.snore.wav_validation import (
    validate_and_extract_wav_metadata,
)


# Dataset-specific Version 1 heuristics derived from three filename-labeled
# examples. These thresholds are not clinically validated.
FRAME_DURATION_SECONDS = 0.5
FRAME_OVERLAP_RATIO = 0.5
ACTIVE_RMS_THRESHOLD = 0.01
SPECTRAL_CENTROID_THRESHOLD_HZ = 800.0
SPECTRAL_FLATNESS_MAX = 0.06
MIN_SNORE_LIKE_ACTIVE_FRACTION = 0.20
MIN_CONSECUTIVE_SNORE_LIKE_FRAMES = 2

_PCM_16_SCALE = 32768.0
_SPECTRAL_EPSILON = 1e-20


@dataclass(frozen=True)
class FrameFeatures:
    rms: float
    spectral_centroid_hz: float
    spectral_flatness: float

    @property
    def is_active(self) -> bool:
        return self.rms >= ACTIVE_RMS_THRESHOLD

    @property
    def is_snore_like(self) -> bool:
        return (
            self.is_active
            and self.spectral_centroid_hz >= SPECTRAL_CENTROID_THRESHOLD_HZ
            and self.spectral_flatness <= SPECTRAL_FLATNESS_MAX
        )


@dataclass(frozen=True)
class SnoreDetection:
    snore_detected: bool
    confidence: float


def decode_pcm16_mono(audio_bytes: bytes) -> tuple[NDArray[np.float64], int]:
    """Validate and decode Version 1 WAV bytes into normalized mono samples."""
    metadata = validate_and_extract_wav_metadata(audio_bytes)

    with wave.open(BytesIO(audio_bytes), "rb") as wav_file:
        frame_bytes = wav_file.readframes(metadata.frame_count)

    samples = np.frombuffer(frame_bytes, dtype="<i2").astype(np.float64)
    samples /= _PCM_16_SCALE
    return samples, metadata.sample_rate


def extract_frame_features(
    samples: NDArray[np.float64],
    sample_rate: int,
) -> tuple[FrameFeatures, ...]:
    """Extract deterministic time and spectral features from overlapping frames."""
    frame_size = int(FRAME_DURATION_SECONDS * sample_rate)
    hop_size = int(frame_size * (1.0 - FRAME_OVERLAP_RATIO))
    window = np.hanning(frame_size)
    frequencies = np.fft.rfftfreq(frame_size, d=1.0 / sample_rate)
    features: list[FrameFeatures] = []

    for start in range(0, len(samples) - frame_size + 1, hop_size):
        frame = samples[start : start + frame_size]
        centered_frame = frame - np.mean(frame)
        rms = float(np.sqrt(np.mean(centered_frame * centered_frame)))

        spectrum = np.fft.rfft(centered_frame * window)
        power = np.abs(spectrum) ** 2
        total_power = float(np.sum(power))

        if total_power <= _SPECTRAL_EPSILON:
            spectral_centroid_hz = 0.0
            spectral_flatness = 1.0
        else:
            spectral_centroid_hz = float(
                np.sum(frequencies * power) / total_power
            )
            non_dc_power = power[1:]
            spectral_flatness = float(
                np.exp(np.mean(np.log(non_dc_power + _SPECTRAL_EPSILON)))
                / (np.mean(non_dc_power) + _SPECTRAL_EPSILON)
            )

        features.append(
            FrameFeatures(
                rms=rms,
                spectral_centroid_hz=spectral_centroid_hz,
                spectral_flatness=spectral_flatness,
            )
        )

    return tuple(features)


def classify_frame_features(
    features: tuple[FrameFeatures, ...],
) -> SnoreDetection:
    """Classify a clip from frame features using Version 1 heuristic thresholds."""
    active_features = tuple(feature for feature in features if feature.is_active)
    if not active_features:
        return SnoreDetection(snore_detected=False, confidence=0.0)

    snore_like_count = sum(feature.is_snore_like for feature in active_features)
    confidence = snore_like_count / len(active_features)

    longest_run = 0
    current_run = 0
    for feature in features:
        if feature.is_snore_like:
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0

    snore_detected = (
        confidence >= MIN_SNORE_LIKE_ACTIVE_FRACTION
        and longest_run >= MIN_CONSECUTIVE_SNORE_LIKE_FRAMES
    )
    return SnoreDetection(
        snore_detected=snore_detected,
        confidence=float(confidence),
    )


def detect_snore(audio_bytes: bytes) -> SnoreDetection:
    """Run the pure Version 1 WAV decoding, feature, and detection pipeline."""
    samples, sample_rate = decode_pcm16_mono(audio_bytes)
    features = extract_frame_features(samples, sample_rate)
    return classify_frame_features(features)
