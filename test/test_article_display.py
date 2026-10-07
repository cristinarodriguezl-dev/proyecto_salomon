from src.models.article import Article
from src.ui.article_display import ArticleDisplay


def test_show_enriched_prints_header_title_and_full_text(capsys):
    article = Article(
        title="Python",
        paragraphs=["p1"],
        enriched="Texto enriquecido completo.\n\nSegundo párrafo.",
    )

    ArticleDisplay().show_enriched(article)

    output = capsys.readouterr().out
    assert ArticleDisplay.ENRICHED_HEADER in output
    assert "Tema: Python" in output
    assert "Texto enriquecido completo.\n\nSegundo párrafo." in output


def test_show_enriched_without_content_prints_clear_message(capsys):
    article = Article(title="Python", paragraphs=["p1"])

    ArticleDisplay().show_enriched(article)

    output = capsys.readouterr().out
    assert ArticleDisplay.EMPTY_ENRICHED_MESSAGE in output
    assert ArticleDisplay.ENRICHED_HEADER not in output