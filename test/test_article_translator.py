"""Pruebas de la traducción por párrafos del artículo."""

from unittest.mock import Mock, call

import pytest

from src.exceptions import TranslationError
from src.models.article import Article
from src.translation.article_translator import ArticleTranslator
from src.translation.translation_service import TranslationService


def test_translates_enriched_paragraphs_in_order_without_changing_source() -> None:
    service = Mock(spec=TranslationService)
    service.translate.side_effect = ["First.", "Second.", "Third."]
    article = Article(
        title="Tema",
        paragraphs=["Original uno.", "Original dos."],
        enriched="Primero.\r\n\r\nSegundo.\r\n   \r\nTercero.",
    )
    source = article.enriched

    result = ArticleTranslator(service).translate(article, "en")

    assert result is article
    assert article.translated == "First.\n\nSecond.\n\nThird."
    assert article.enriched == source
    assert article.paragraphs == ["Original uno.", "Original dos."]
    assert service.translate.call_args_list == [
        call("Primero.", "en"),
        call("Segundo.", "en"),
        call("Tercero.", "en"),
    ]


def test_uses_original_paragraphs_when_enrichment_is_unavailable() -> None:
    service = Mock(spec=TranslationService)
    service.translate.side_effect = ["First.", "Second."]
    article = Article(title="Tema", paragraphs=["Primero.", "Segundo."])

    ArticleTranslator(service).translate(article, "en")

    assert article.translated == "First.\n\nSecond."
    assert article.enriched == ""
    assert article.paragraphs == ["Primero.", "Segundo."]


def test_failure_does_not_save_an_incomplete_translation() -> None:
    service = Mock(spec=TranslationService)
    service.translate.side_effect = ["First.", TranslationError("MyMemory unavailable")]
    article = Article(
        title="Tema",
        paragraphs=["Original."],
        enriched="Primero.\n\nSegundo.",
        translated="Previous complete translation.",
    )

    with pytest.raises(TranslationError, match="MyMemory unavailable"):
        ArticleTranslator(service).translate(article, "en")

    assert article.translated == "Previous complete translation."
    assert article.enriched == "Primero.\n\nSegundo."


def test_rejects_article_without_paragraphs() -> None:
    service = Mock(spec=TranslationService)
    article = Article(title="Tema", paragraphs=[])

    with pytest.raises(ValueError, match="No hay párrafos"):
        ArticleTranslator(service).translate(article, "en")

    service.translate.assert_not_called()
