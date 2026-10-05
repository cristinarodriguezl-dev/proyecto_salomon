import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    wikipedia_timeout: int

def load_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        wikipedia_timeout=int(os.getenv("WIKIPEDIA_TIMEOUT", "")),
    )