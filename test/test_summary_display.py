"""Pruebas de la presentación del resumen en la terminal."""

from src.models.article import Article
from src.ui.summary_display import EMPTY_SUMMARY_MESSAGE, SUMMARY_HEADER, show_summary


def test_show_summary_outputs_header_and_full_text(capsys) -> None:
    article = Article(
        title="Árbol",
        paragraphs=["Primer párrafo."],
        summary="Idea principal.\n\nSegunda idea.",
    )

    show_summary(article)

    assert capsys.readouterr().out == (
        f"{SUMMARY_HEADER}\n\nIdea principal.\n\nSegunda idea.\n"
    )


def test_show_summary_without_content_outputs_clear_message(capsys) -> None:
    article = Article(title="Árbol", paragraphs=["Primer párrafo."])

    show_summary(article)

    assert capsys.readouterr().out == f"{EMPTY_SUMMARY_MESSAGE}\n"