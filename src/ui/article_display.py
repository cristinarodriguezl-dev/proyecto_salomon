"""Muestra el contenido original de un artículo en la terminal."""

from src.models.article import Article


def show_original_article(article: Article) -> None:
    """Muestra el título y los párrafos originales de un artículo."""
    print(article.title)
    print()

    for paragraph in article.paragraphs:
        print(paragraph)
