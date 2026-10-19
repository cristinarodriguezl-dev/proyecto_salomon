import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

INVALID_TIMEOUT_MESSAGE = "WIKIPEDIA_TIMEOUT debe ser un entero mayor que cero."


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    wikipedia_timeout: int


def load_settings() -> Settings:
    try:
        wikipedia_timeout = int(os.getenv("WIKIPEDIA_TIMEOUT", "10"))
    except ValueError as error:
        raise ValueError(INVALID_TIMEOUT_MESSAGE) from error

    if wikipedia_timeout <= 0:
        raise ValueError(INVALID_TIMEOUT_MESSAGE)

    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        wikipedia_timeout=wikipedia_timeout,
    )
