"""Extrae información del HTML recibido desde Wikipedia."""

from bs4 import BeautifulSoup


class WikipediaParser:
    """Procesa el HTML de un artículo sin realizar peticiones HTTP."""

    def extract_title(self, html: str) -> str:
        """Devuelve el título principal del artículo de Wikipedia."""
        soup = BeautifulSoup(html, "html.parser")
        title_element = soup.find("h1", id="firstHeading")
        title = title_element.get_text(" ", strip=True) if title_element else ""

        if not title:
            raise ValueError(
                "No se encontró un título válido en la respuesta de Wikipedia."
            )

        return title
