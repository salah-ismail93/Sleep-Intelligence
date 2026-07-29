from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_valid_chat_request_returns_200_and_placeholder():
    payload = {"message": "Hello, how was my sleep?"}

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert response.json() == {"reply": "Chat service placeholder response."}


@pytest.mark.parametrize(
    "invalid_message",
    [
        "",  # Empty string
        "   ",  # Whitespace only
        "\t\n  ",  # Tabs and newlines only
    ],
)
def test_empty_or_whitespace_message_returns_422(invalid_message: str):
    payload = {"message": invalid_message}

    response = client.post("/chat", json=payload)

    assert response.status_code == 422


def test_message_exceeding_max_length_returns_422():
    payload = {"message": "a" * 2001}  # Exceeds 2000 character limit

    response = client.post("/chat", json=payload)

    assert response.status_code == 422