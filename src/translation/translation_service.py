"""Traducción de un texto con el servicio HTTP de MyMemory."""

import html
import time

import requests

from src.exceptions import TranslationError


SUPPORTED_LANGUAGES = {
    "de": "Alemán",
    "en": "Inglés",
    "es": "Español",
    "fr": "Francés",
    "it": "Italiano",
    "pt": "Portugués",
}


class TranslationService:
    """Traduce un texto o párrafo por llamada a MyMemory."""

    API_URL = "https://api.mymemory.translated.net/get"
    MAX_CHUNK_SIZE = 450
    REQUEST_TIMEOUT = 20

    def get_supported_languages(self) -> dict[str, str]:
        """Devuelve los idiomas disponibles en el selector del proyecto."""
        return SUPPORTED_LANGUAGES.copy()

    def translate(
        self,
        content: str,
        target_language: str,
        source_language: str = "es",
    ) -> str:
        """Traduce un texto; el llamador gestiona los párrafos del artículo."""
        if not isinstance(content, str) or not content.strip():
            raise ValueError("No hay contenido para traducir.")

        source = self._normalize_language(source_language)
        target = self._normalize_language(target_language)
        if source == target:
            return content

        chunks = self._split_text(" ".join(content.split()))
        translated_chunks = []

        for index, chunk in enumerate(chunks):
            if index:
                time.sleep(0.5)
            try:
                response = requests.get(
                    self.API_URL,
                    params={"q": chunk, "langpair": f"{source}|{target}"},
                    timeout=self.REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as error:
                raise TranslationError(
                    f"No se pudo consultar MyMemory: {error}"
                ) from error
            except (TypeError, ValueError, AttributeError) as error:
                raise TranslationError(
                    "MyMemory devolvió una respuesta no válida."
                ) from error

            if not isinstance(data, dict) or data.get("responseStatus") != 200:
                detail = (
                    data.get("responseDetails", "Error desconocido de MyMemory.")
                    if isinstance(data, dict)
                    else "MyMemory devolvió una respuesta no válida."
                )
                raise TranslationError(f"Error de MyMemory: {detail}")

            response_data = data.get("responseData")
            translated = (
                response_data.get("translatedText")
                if isinstance(response_data, dict)
                else None
            )
            if not isinstance(translated, str) or not translated.strip():
                raise TranslationError(
                    "MyMemory no ha devuelto una traducción."
                )
            translated_chunks.append(html.unescape(translated))

        return " ".join(translated_chunks)

    @staticmethod
    def _normalize_language(language: str) -> str:
        """Valida y normaliza un código o nombre admitido por el selector."""
        if not isinstance(language, str) or not language.strip():
            raise ValueError("Debes indicar un idioma válido.")

        value = language.strip().casefold()
        for code, name in SUPPORTED_LANGUAGES.items():
            if value in (code.casefold(), name.casefold()):
                return code

        raise ValueError(f"Idioma no admitido: {language}.")

    def _split_text(self, content: str) -> list[str]:
        """Divide el texto en bloques aceptados por MyMemory sin cortar palabras."""
        chunks: list[str] = []
        current = ""

        for word in content.split():
            if len(word) > self.MAX_CHUNK_SIZE:
                raise ValueError(
                    "Una palabra supera el límite de tamaño de traducción."
                )

            candidate = f"{current} {word}".strip()
            if len(candidate) > self.MAX_CHUNK_SIZE:
                chunks.append(current)
                current = word
            else:
                current = candidate

        if current:
            chunks.append(current)
        return chunks
