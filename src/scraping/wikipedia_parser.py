"""Extrae información del HTML recibido desde Wikipedia."""

from bs4 import BeautifulSoup


ARTICLE_CONTENT_SELECTOR = "#mw-content-text .mw-parser-output"
EXCLUDED_ANCESTOR_TAGS = ["aside", "footer", "nav", "table"]
EXCLUDED_CONTAINER_CLASSES = ["ambox", "hatnote", "infobox", "metadata", "navbox"]
MAX_PARAGRAPHS = 5


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

    def extract_paragraphs(self, html: str) -> list[str]:
        """Devuelve hasta cinco párrafos con texto del contenido principal."""
        soup = BeautifulSoup(html, "html.parser")
        content = soup.select_one(ARTICLE_CONTENT_SELECTOR)

        if content is None:
            return []

        paragraphs: list[str] = []

        for paragraph in content.find_all("p"):
            belongs_to_excluded_content = paragraph.find_parent(
                EXCLUDED_ANCESTOR_TAGS
            ) or paragraph.find_parent(class_=EXCLUDED_CONTAINER_CLASSES)

            if belongs_to_excluded_content:
                continue

            text = paragraph.get_text(" ", strip=True)
            if text:
                paragraphs.append(text)

            if len(paragraphs) == MAX_PARAGRAPHS:
                break

        return paragraphs
