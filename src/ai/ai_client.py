import httpx
from google import genai
from google.genai import errors, types

from src.exceptions import EnrichmentError

MODEL_NAME = "gemini-3.1-flash-lite"
MISSING_API_KEY_MESSAGE = (
    "Falta la clave de Gemini. Define GEMINI_API_KEY en tu archivo .env."
)
INVALID_API_KEY_MESSAGE = (
    "La clave de Gemini no es válida. Revisa GEMINI_API_KEY en tu archivo .env."
)
TIMEOUT_MESSAGE = "Gemini tardó demasiado en responder (tiempo de espera agotado)."
RATE_LIMIT_MESSAGE = (
    "Se alcanzó el límite de uso de Gemini. Espera un poco antes de volver a intentarlo."
)
SERVICE_ERROR_MESSAGE = "El servicio de Gemini no está disponible en este momento."
NETWORK_ERROR_MESSAGE = (
    "No se pudo conectar con Gemini. Revisa tu conexión a internet."
)


def _message_for_api_error(error):
    """Return the user-facing message that matches a Gemini API error."""
    if error.code in (401, 403) or (
        error.code == 400 and "API key" in str(error.message)
    ):
        return INVALID_API_KEY_MESSAGE
    if error.code == 429:
        return RATE_LIMIT_MESSAGE
    return SERVICE_ERROR_MESSAGE


class AIClient:
    """Talks to the Gemini API."""

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key) if api_key else None

    def generate_text(self, prompt):
        """Send a prompt to Gemini and return its answer as text."""
        if self.client is None:
            raise EnrichmentError(MISSING_API_KEY_MESSAGE)

        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                ),
            )
            except httpx.TimeoutException as error:
            raise EnrichmentError(TIMEOUT_MESSAGE) from error
        except httpx.TransportError as error:
            raise EnrichmentError(NETWORK_ERROR_MESSAGE) from error
        except errors.APIError as error:
            raise EnrichmentError(_message_for_api_error(error)) from error
