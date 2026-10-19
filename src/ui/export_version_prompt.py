"""Permite elegir qué versión de un artículo se guardará."""

import questionary

from src.models.article import Article


class ExportVersionPrompt:
    """Muestra solo las versiones disponibles y devuelve el texto elegido."""

    MENU_MESSAGE = "\n¿Qué versión quieres guardar?"

    def ask(self, article: Article) -> str:
        """Devuelve el contenido de la versión elegida por el usuario."""
        versions = {"Original": "\n\n".join(article.paragraphs)}

        if article.enriched.strip():
            versions["Enriquecida"] = article.enriched
        if article.translated.strip():
            versions["Traducida"] = article.translated

        choice = questionary.select(
            self.MENU_MESSAGE, choices=list(versions)
        ).unsafe_ask()

        return versions[choice]
