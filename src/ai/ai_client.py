from google import genai
from google.genai import types

from src.exceptions import EnrichmentError

MODEL_NAME = "gemini-3.1-flash-lite"
MISSING_API_KEY_MESSAGE = (
    "Falta la clave de Gemini. Define GEMINI_API_KEY en tu archivo .env."
)


class AIClient:
    """Talks to the Gemini API."""

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key) if api_key else None

    def generate_text(self, prompt):
        """Send a prompt to Gemini and return its answer as text."""
        if self.client is None:
            raise EnrichmentError(MISSING_API_KEY_MESSAGE)

        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            ),
        )
        return response.text