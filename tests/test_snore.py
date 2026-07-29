from io import BytesIO
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_valid_wav_upload_returns_placeholder_response():
    fake_wav_data = b"RIFF....WAVEfmt "  # Dummy WAV bytes
    files = {"audio": ("sample.wav", BytesIO(fake_wav_data), "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 200
    assert response.json() == {
        "snore_detected": False,
        "confidence": 0.0,
    }


def test_non_wav_upload_returns_415():
    fake_mp3_data = b"ID3..."
    files = {"audio": ("sample.mp3", BytesIO(fake_mp3_data), "audio/mpeg")}

    response = client.post("/snore", files=files)

    assert response.status_code == 415


def test_oversized_upload_returns_413():
    # 10 MB + 1 byte payload
    oversized_data = b"0" * (10 * 1024 * 1024 + 1)
    files = {"audio": ("large_sample.wav", BytesIO(oversized_data), "audio/wav")}

    response = client.post("/snore", files=files)

    assert response.status_code == 413