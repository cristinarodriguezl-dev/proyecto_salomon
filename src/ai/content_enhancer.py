from src.ai.prompts import build_enrichment_prompt


class ContentEnhancer:
    """Asks the AI to enrich an article and stores the result in it."""

    def __init__(self, ai_client):
        self.ai_client = ai_client

    def enhance(self, article):
        """Fill article.enriched with the AI-expanded text and return the article."""
        text = "\n\n".join(article.paragraphs)
        prompt = build_enrichment_prompt(article.title, text)
        article.enriched = self.ai_client.generate_text(prompt)
        return article