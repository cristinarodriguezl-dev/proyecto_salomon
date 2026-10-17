"""Coordina la consulta y el procesamiento de un artículo de Wikipedia."""

from src.exceptions import SearchError
from src.models.article import Article
from src.scraping.wikipedia_client import WikipediaClient
from src.scraping.wikipedia_parser import WikipediaParser

NO_ARTICLE_MESSAGE = (
    'No se encontró un artículo válido para "{topic}". Prueba otra búsqueda.'
)


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

        if self.wikipedia_parser.is_disambiguation_page(html):
            raise SearchError(
                f'El tema "{topic}" es ambiguo. '
                "Prueba con un nombre más específico o añade una palabra "
                "que indique a qué te refieres."
            )

        try:
            title = self.wikipedia_parser.extract_title(html)
        except ValueError as error:
            raise SearchError(NO_ARTICLE_MESSAGE.format(topic=topic)) from error

        paragraphs = self.wikipedia_parser.extract_paragraphs(html)
        if not paragraphs:
            raise SearchError(NO_ARTICLE_MESSAGE.format(topic=topic))

        return Article(
            title=title,
            paragraphs=paragraphs,
        )
