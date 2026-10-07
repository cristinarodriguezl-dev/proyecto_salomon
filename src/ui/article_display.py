from src.models.article import Article


class ArticleDisplay:
    """Shows article versions in the terminal under a header that identifies them."""

    ENRICHED_HEADER = "CONTENIDO ENRIQUECIDO (IA)"
    EMPTY_ENRICHED_MESSAGE = "No hay contenido enriquecido para mostrar."
    SEPARATOR = "=" * 60

    def format_enriched(self, article: Article) -> str:
        """Return the enriched text under its header, or a clear message if it is empty."""
        if not article.enriched:
            return self.EMPTY_ENRICHED_MESSAGE

        return "\n".join(
            [
                self.SEPARATOR,
                self.ENRICHED_HEADER,
                f"Tema: {article.title}",
                self.SEPARATOR,
                article.enriched,
            ]
        )

    def show_enriched(self, article: Article) -> None:
        """Print the enriched text in the terminal."""
        print(self.format_enriched(article))