"""Consulta páginas de Wikipedia para el tema solicitado."""

import requests


WIKIPEDIA_SEARCH_URL = "https://es.wikipedia.org/w/index.php"
USER_AGENT = "Salomon/0.1 (https://github.com/cristinarodriguezl-dev/proyecto_salomon)"


class WikipediaClient:
    """Realiza la consulta HTTP sin procesar el contenido de la respuesta."""

    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, topic: str) -> requests.Response:
        """Devuelve la respuesta de Wikipedia o informa de un timeout."""
        try:
            return requests.get(
                WIKIPEDIA_SEARCH_URL,
                params={"search": topic},
                headers={"User-Agent": USER_AGENT},
                timeout=self.timeout_seconds,
            )
        except requests.exceptions.Timeout as exc:
            raise TimeoutError(
                "La consulta a Wikipedia superó el tiempo de espera de "
                f"{self.timeout_seconds:g} segundos."
            ) from exc
