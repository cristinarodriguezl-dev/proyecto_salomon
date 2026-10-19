"""Traduce un artículo sin perder el orden ni la separación de sus párrafos."""

import re

from src.models.article import Article
from src.translation.translation_service import TranslationService


class ArticleTranslator:
    """Guarda en Article la traducción completa de su versión disponible."""

    def __init__(self, translation_service: TranslationService) -> None:
        self.translation_service = translation_service

    def translate(self, article: Article, target_language: str) -> Article:
        """Prefiere el enriquecido; usa el original si Gemini no lo produjo."""
        if article.enriched.strip():
            paragraphs = re.split(
                r"\r?\n(?:[ \t]*\r?\n)+", article.enriched.strip()
            )
        else:
            paragraphs = article.paragraphs

        paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
        if not paragraphs:
            raise ValueError("No hay párrafos para traducir.")

        translated_paragraphs = [
            self.translation_service.translate(paragraph, target_language)
            for paragraph in paragraphs
        ]
        article.translated = "\n\n".join(translated_paragraphs)
        return article
