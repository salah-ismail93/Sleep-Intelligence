import io
import wave
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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


def test_valid_in_memory_wav_returns_200_and_schema():
    wav_bytes = create_valid_wav_bytes(sample_rate=16000, num_frames=16000)
    files = {"audio": ("test.wav", wav_bytes, "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp == {
        "snore_detected": False,
        "confidence": 0.0,
    }


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