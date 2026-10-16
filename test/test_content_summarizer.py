from unittest.mock import Mock

import pytest

from src.ai.content_summarizer import NO_ENRICHED_CONTENT_MESSAGE, ContentSummarizer
from src.exceptions import EnrichmentError
from src.models.article import Article


def make_article():
    return Article(
        title="Python",
        paragraphs=["First.", "Second."],
        enriched="Enriched text.",
        translated="Texto traducido.",
    )


def test_summarize_stores_summary_in_article():
    ai_client = Mock()
    ai_client.generate_text.return_value = "Summary text"

    result = ContentSummarizer(ai_client).summarize(make_article())

    assert result.summary == "Summary text"
    prompt_sent = ai_client.generate_text.call_args[0][0]
    assert "Python" in prompt_sent
    assert "Enriched text." in prompt_sent


def test_summarize_keeps_the_other_versions_unchanged():
    ai_client = Mock()
    ai_client.generate_text.return_value = "Summary text"

    result = ContentSummarizer(ai_client).summarize(make_article())

    assert result.paragraphs == ["First.", "Second."]
    assert result.enriched == "Enriched text."
    assert result.translated == "Texto traducido."


def test_summarize_without_enriched_content_raises_clear_error():
    ai_client = Mock()
    article = Article(title="Python", paragraphs=["First."])

    with pytest.raises(EnrichmentError) as raised:
        ContentSummarizer(ai_client).summarize(article)

    assert str(raised.value) == NO_ENRICHED_CONTENT_MESSAGE
    ai_client.generate_text.assert_not_called()


def test_summarize_keeps_the_article_unchanged_when_the_ai_fails():
    ai_client = Mock()
    ai_client.generate_text.side_effect = EnrichmentError("Gemini failed")
    article = make_article()

    with pytest.raises(EnrichmentError, match="Gemini failed"):
        ContentSummarizer(ai_client).summarize(article)

    assert article.summary == ""
    assert article.enriched == "Enriched text."
