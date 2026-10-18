"""Muestra en la terminal el resumen de un artículo."""

from src.models.article import Article

SUMMARY_HEADER = "RESUMEN (IA)"
EMPTY_SUMMARY_MESSAGE = "No hay resumen para mostrar."


def show_summary(article: Article) -> None:
    """Muestra el resumen con IA bajo un encabezado que lo identifica."""
    if not article.summary:
        print(EMPTY_SUMMARY_MESSAGE)
        return

    print(SUMMARY_HEADER)
    print()
    print(article.summary)