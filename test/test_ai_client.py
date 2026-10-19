from unittest.mock import patch

import pytest
from google.genai import types

from src.ai.ai_client import AIClient, MODEL_NAME
from src.exceptions import EnrichmentError


@patch("src.ai.ai_client.genai.Client")
def test_generate_text_returns_gemini_answer(mock_client_class):
    mock_client = mock_client_class.return_value
    mock_client.models.generate_content.return_value.text = "Hello!"

    client = AIClient("fake-key")
    answer = client.generate_text("Say hello")

    mock_client_class.assert_called_once_with(api_key="fake-key")
    mock_client.models.generate_content.assert_called_once_with(
        model=MODEL_NAME,
        contents="Say hello",
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        ),
    )
    assert answer == "Hello!"


@pytest.mark.parametrize("api_key", ["", None])
def test_generate_text_without_api_key_raises_enrichment_error(api_key):
    with patch("src.ai.ai_client.genai.Client") as mock_client_class:
        client = AIClient(api_key)

        with pytest.raises(EnrichmentError, match="GEMINI_API_KEY"):
            client.generate_text("Say hello")

    mock_client_class.assert_not_called()
