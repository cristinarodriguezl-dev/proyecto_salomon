from src.ai.prompts import build_summary_prompt
from src.exceptions import EnrichmentError

NO_ENRICHED_CONTENT_MESSAGE = "No hay contenido enriquecido que resumir."


class ContentSummarizer:
    """Asks the AI to summarize the enriched text and stores it in the article."""

    def __init__(self, ai_client):
        self.ai_client = ai_client

    def summarize(self, article):
        """Fill article.summary with a summary of the enriched text and return it."""
        if not article.enriched.strip():
            raise EnrichmentError(NO_ENRICHED_CONTENT_MESSAGE)

        prompt = build_summary_prompt(article.title, article.enriched)
        article.summary = self.ai_client.generate_text(prompt)
        return article
