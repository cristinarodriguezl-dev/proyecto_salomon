from unittest.mock import patch

from src.ai.ai_client import AIClient, MODEL_NAME


@patch("src.ai.ai_client.genai.Client")
def test_generate_text_returns_gemini_answer(mock_client_class):
    mock_client = mock_client_class.return_value
    mock_client.models.generate_content.return_value.text = "Hello!"

    client = AIClient("fake-key")
    answer = client.generate_text("Say hello")

    mock_client_class.assert_called_once_with(api_key="fake-key")
    mock_client.models.generate_content.assert_called_once_with(
        model=MODEL_NAME, contents="Say hello"
    )
    assert answer == "Hello!"