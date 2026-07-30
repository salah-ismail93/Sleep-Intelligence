import pytest
from pydantic import ValidationError

from app.api.models.chat import ChatRequest, ChatResponse


def test_valid_chat_request():
    req = ChatRequest(message="How can I improve my sleep environment?")
    assert req.message == "How can I improve my sleep environment?"


def test_empty_message_raises_validation_error():
    with pytest.raises(ValidationError):
        ChatRequest(message="")


def test_whitespace_only_message_raises_validation_error():
    with pytest.raises(ValidationError):
        ChatRequest(message="   \n\t  ")


def test_message_exceeding_max_length_raises_validation_error():
    with pytest.raises(ValidationError):
        ChatRequest(message="a" * 2001)


def test_chat_response_schema():
    resp = ChatResponse(reply="Keep your bedroom dark and cool.")
    assert resp.reply == "Keep your bedroom dark and cool."