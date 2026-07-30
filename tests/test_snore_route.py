import io
import math
import struct
import wave
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_tone_wav_bytes(
    freq_hz: float,
    duration_s: float = 1.0,
    sample_rate: int = 16000,
    amplitude: float = 0.5,
) -> bytes:
    """Generates in-memory PCM 16-bit mono WAV bytes for a given sine wave frequency."""
    num_samples = int(sample_rate * duration_s)
    buf = io.BytesIO()

    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)

        max_int16 = 32767
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            sample_val = int(amplitude * max_int16 * math.sin(2 * math.pi * freq_hz * t))
            frames.extend(struct.pack("<h", sample_val))

        w.writeframes(frames)

    return buf.getvalue()


def create_valid_wav_bytes(
    sample_rate: int = 16000,
    channels: int = 1,
    sampwidth: int = 2,
    num_frames: int = 16000,
) -> bytes:
    """Helper fixture to build a valid in-memory PCM WAV file."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sample_rate)
        w.writeframes(b"\x00" * (num_frames * channels * sampwidth))
    return buf.getvalue()


# --- Endpoint Tests ---

def test_1khz_active_tone_returns_snore_detected_true():
    # Active snore tone (1 kHz) within duration/amplitude limits
    wav_bytes = create_tone_wav_bytes(freq_hz=1000.0, duration_s=1.0)
    files = {"audio": ("snore.wav", wav_bytes, "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["snore_detected"] is True
    assert json_resp["confidence"] > 0.0


def test_200hz_active_tone_returns_snore_detected_false():
    # Inactive frequency tone (200 Hz) outside target snore band
    wav_bytes = create_tone_wav_bytes(freq_hz=200.0, duration_s=1.0)
    files = {"audio": ("nonsnore.wav", wav_bytes, "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["snore_detected"] is False


def test_wrong_file_extension_returns_415():
    files = {"audio": ("test.mp3", b"fake audio content", "audio/mpeg")}

    response = client.post("/snore", files=files)

    assert response.status_code == 415
    assert "Only .wav files are allowed" in response.json()["detail"]


def test_non_wav_content_named_wav_returns_415():
    files = {"audio": ("invalid.wav", b"NOT_A_REAL_WAV_HEADER_DATA_STREAM", "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 415
    assert "RIFF/WAVE container" in response.json()["detail"]


def test_unsupported_wav_properties_returns_422():
    stereo_wav = create_valid_wav_bytes(channels=2)
    files = {"audio": ("stereo.wav", stereo_wav, "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 422
    assert "Only mono" in response.json()["detail"]


def test_malformed_truncated_wav_returns_422():
    valid_wav = create_valid_wav_bytes()
    truncated_wav = valid_wav[:30]
    files = {"audio": ("truncated.wav", truncated_wav, "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 422


def test_file_over_10mib_returns_413():
    oversized_bytes = b"\x00" * (10 * 1024 * 1024 + 1)
    files = {"audio": ("huge.wav", oversized_bytes, "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 413
    assert "10 MiB limit" in response.json()["detail"]