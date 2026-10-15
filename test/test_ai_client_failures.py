"""Tests for the messages AIClient raises when Gemini fails."""

from unittest.mock import patch

import httpx
import pytest
from google.genai import errors

from src.ai.ai_client import (
    INVALID_API_KEY_MESSAGE,
    NETWORK_ERROR_MESSAGE,
    RATE_LIMIT_MESSAGE,
    SERVICE_ERROR_MESSAGE,
    TIMEOUT_MESSAGE,
    AIClient,
)
from src.exceptions import EnrichmentError


def make_client_error(code, message):
    return errors.ClientError(code, {"error": {"code": code, "message": message}})


def make_server_error(code, message):
    return errors.ServerError(code, {"error": {"code": code, "message": message}})


GEMINI_FAILURES = [
    (
        make_client_error(400, "API key not valid. Please pass a valid API key."),
        INVALID_API_KEY_MESSAGE,
    ),
    (make_client_error(403, "Permission denied."), INVALID_API_KEY_MESSAGE),
    (httpx.ReadTimeout("timed out"), TIMEOUT_MESSAGE),
    (httpx.ConnectError("no connection"), NETWORK_ERROR_MESSAGE),
    (make_client_error(429, "Quota exceeded."), RATE_LIMIT_MESSAGE),
    (make_server_error(503, "Service unavailable."), SERVICE_ERROR_MESSAGE),
]
FAILURE_IDS = [
    "invalid_key_400",
    "invalid_key_403",
    "timeout",
    "network",
    "rate_limit",
    "server",
]


@pytest.mark.parametrize(
    ("gemini_error", "expected_message"), GEMINI_FAILURES, ids=FAILURE_IDS
)
@patch("src.ai.ai_client.genai.Client")
def test_generate_text_translates_gemini_failures(
    mock_client_class, gemini_error, expected_message
):
    mock_client_class.return_value.models.generate_content.side_effect = gemini_error

    with pytest.raises(EnrichmentError) as raised:
        AIClient("fake-key").generate_text("Say hello")

    assert str(raised.value) == expected_message