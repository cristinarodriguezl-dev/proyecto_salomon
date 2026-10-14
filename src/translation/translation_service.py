"""Servicio de traducción mediante la API de MyMemory."""

import html
import time

import requests


class TranslationService:
    """Traduce textos utilizando MyMemory."""

    API_URL = "https://api.mymemory.translated.net/get"
    MAX_CHUNK_SIZE = 450

    def translate(
        self,
        content: str,
        target_language: str,
        source_language: str = "es",
    ) -> str:
        """Traduce el contenido al idioma solicitado."""
        if not content or not content.strip():
            raise ValueError("No hay contenido para traducir.")

        source_language = source_language.strip().lower()
        target_language = target_language.strip().lower()

        if not source_language or not target_language:
            raise ValueError("Debes indicar ambos idiomas.")

        if source_language == target_language:
            return content

        chunks = self._split_text(content)
        translated_chunks = []

        for index, chunk in enumerate(chunks):
            if index > 0:
                time.sleep(0.5)

            response = requests.get(
                self.API_URL,
                params={
                    "q": chunk,
                    "langpair": f"{source_language}|{target_language}",
                },
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("responseStatus") != 200:
                detail = data.get(
                    "responseDetails",
                    "Error desconocido de MyMemory.",
                )
                raise RuntimeError(f"Error de MyMemory: {detail}")

            translated = data.get("responseData", {}).get(
                "translatedText"
            )

            if not translated:
                raise RuntimeError(
                    "MyMemory no ha devuelto una traducción."
                )

            translated_chunks.append(html.unescape(translated))

        return " ".join(translated_chunks)

    def _split_text(self, content: str) -> list[str]:
        """Divide el texto en fragmentos sin cortar palabras."""
        chunks = []
        current_chunk = ""

        for word in content.split():
            candidate = f"{current_chunk} {word}".strip()

            if len(candidate) > self.MAX_CHUNK_SIZE:
                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = word
            else:
                current_chunk = candidate

        if current_chunk:
            chunks.append(current_chunk)

        return chunks