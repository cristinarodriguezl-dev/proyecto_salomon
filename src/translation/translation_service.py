import requests


class TranslationService:
    """Servicio encargado de traducir contenido mediante MyMemory."""

    def __init__(self):
        self.url = "https://api.mymemory.translated.net/get"

    def translate(self, content: str, language: str) -> str:
        """
        Traduce un contenido utilizando la API de MyMemory.
        """

        source_language = "es"

        translated_parts = []

        # Dividimos el contenido en fragmentos
        # para evitar superar el límite de MyMemory.
        chunks = self._split_text(content, 400)

        for chunk in chunks:

            params = {
                "q": chunk,
                "langpair": f"{source_language}|{language}"
            }

            response = requests.get(
                self.url,
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(
                    f"Error de MyMemory: "
                    f"{response.status_code} - {response.text}"
                )

            data = response.json()

            response_status = data.get("responseStatus")

            if response_status != 200:
                raise Exception(
                    f"MyMemory no pudo traducir el texto: "
                    f"{data.get('responseDetails')}"
                )

            translated_text = data.get("responseData", {}).get(
                "translatedText"
            )

            if not translated_text:
                raise ValueError(
                    "MyMemory no devolvió contenido traducido."
                )

            translated_parts.append(translated_text)

        return "\n\n".join(translated_parts)

    @staticmethod
    def _split_text(text: str, max_length: int) -> list[str]:
        """
        Divide el texto en fragmentos pequeños.
        Intenta respetar los saltos de párrafo.
        """

        paragraphs = text.split("\n")

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:

            if len(current_chunk) + len(paragraph) + 1 <= max_length:
                current_chunk += paragraph + "\n"

            else:

                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                current_chunk = paragraph + "\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks