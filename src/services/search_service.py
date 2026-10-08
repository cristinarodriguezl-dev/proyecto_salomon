"""Coordina la consulta y el procesamiento de un artículo de Wikipedia."""

from src.models.article import Article
from src.scraping.wikipedia_client import WikipediaClient
from src.scraping.wikipedia_parser import WikipediaParser


class WikipediaSearchService:
    """Obtiene y convierte una respuesta de Wikipedia en un Article."""

    def __init__(
        self,
        wikipedia_client: WikipediaClient | None = None,
        wikipedia_parser: WikipediaParser | None = None,
    ) -> None:
        self.wikipedia_client = (
            wikipedia_client if wikipedia_client is not None else WikipediaClient()
        )
        self.wikipedia_parser = (
            wikipedia_parser if wikipedia_parser is not None else WikipediaParser()
        )

    def search(self, topic: str) -> Article:
        """Busca un tema y devuelve el artículo con su título y párrafos."""
        response = self.wikipedia_client.fetch(topic)
        html = response.text
        suggestion = self.wikipedia_parser.extract_suggestion(html)

        return Article(
            title=self.wikipedia_parser.extract_title(html),
            paragraphs=self.wikipedia_parser.extract_paragraphs(html),
            suggestion=suggestion,
        )
