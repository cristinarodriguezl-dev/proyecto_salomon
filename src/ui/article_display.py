"""Muestra en la terminal las distintas versiones de un artículo."""

from src.models.article import Article

ENRICHED_HEADER = "CONTENIDO ENRIQUECIDO (IA)"
EMPTY_ENRICHED_MESSAGE = "No hay contenido enriquecido para mostrar."


def show_original_article(article: Article) -> None:
    """Muestra el título y los párrafos originales de un artículo."""
    print(article.title)
    print()

    for paragraph in article.paragraphs:
        print(paragraph)


def show_enriched_article(article: Article) -> None:
    """Muestra el contenido enriquecido con IA bajo un encabezado que lo identifica."""
    if not article.enriched:
        print(EMPTY_ENRICHED_MESSAGE)
        return

    print(ENRICHED_HEADER)
    print()
    print(article.enriched)