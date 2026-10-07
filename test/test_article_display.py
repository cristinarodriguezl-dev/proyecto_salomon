"""Pruebas de la presentación del contenido original en la terminal."""

from src.models.article import Article
from src.ui.article_display import show_original_article


def test_show_original_article_outputs_title_and_all_paragraphs(capsys) -> None:
    article = Article(
        title="Árbol",
        paragraphs=["Primer párrafo.", "Segundo párrafo."],
    )

    show_original_article(article)

    assert capsys.readouterr().out == (
        "Árbol\n\nPrimer párrafo.\nSegundo párrafo.\n"
    )
