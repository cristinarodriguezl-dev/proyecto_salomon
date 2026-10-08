from unittest.mock import Mock

from src.ai.content_enhancer import ContentEnhancer
from src.models.article import Article


def test_enhance_stores_enriched_text_in_article():
    ai_client = Mock()
    ai_client.generate_text.return_value = "Enriched text"
    article = Article(title="Python", paragraphs=["First.", "Second."])

    result = ContentEnhancer(ai_client).enhance(article)

    assert result.enriched == "Enriched text"
    prompt_sent = ai_client.generate_text.call_args[0][0]
    assert "Python" in prompt_sent
    assert "First." in prompt_sent