"""Pruebas de la presentación del contenido original y enriquecido en la terminal."""

from src.models.article import Article
from src.ui.article_display import (
    EMPTY_ENRICHED_MESSAGE,
    ENRICHED_HEADER,
    show_enriched_article,
    show_original_article,
)


def test_show_original_article_outputs_title_and_all_paragraphs(capsys) -> None:
    article = Article(
        title="Árbol",
        paragraphs=["Primer párrafo.", "Segundo párrafo."],
    )

    show_original_article(article)

    assert capsys.readouterr().out == (
        "Árbol\n\nPrimer párrafo.\nSegundo párrafo.\n"
    )


def test_show_enriched_article_outputs_header_and_full_text(capsys) -> None:
    article = Article(
        title="Árbol",
        paragraphs=["Primer párrafo."],
        enriched="Texto enriquecido.\n\nSegundo párrafo enriquecido.",
    )

    show_enriched_article(article)

    assert capsys.readouterr().out == (
        f"{ENRICHED_HEADER}\n\nTexto enriquecido.\n\nSegundo párrafo enriquecido.\n"
    )


def test_show_enriched_article_without_content_outputs_clear_message(capsys) -> None:
    article = Article(title="Árbol", paragraphs=["Primer párrafo."])

    show_enriched_article(article)

    assert capsys.readouterr().out == f"{EMPTY_ENRICHED_MESSAGE}\n"