"""Coordina búsqueda, enriquecimiento, traducción y exportación."""

import requests

from src.ai.ai_client import AIClient
from src.ai.content_enhancer import ContentEnhancer
from src.export.exporter import Exporter
from src.services.search_service import WikipediaSearchService
from src.settings import load_settings
from src.translation.translation_service import TranslationService
from src.ui.article_display import (
    show_enriched_article,
    show_original_article,
)
from src.ui.export_input import request_export_format
from src.ui.topic_input import request_topic
from src.ui.translation_input import request_target_language


def main() -> None:
    """Ejecuta el flujo completo del artículo."""
    search_service = WikipediaSearchService()
    content_enhancer = ContentEnhancer(
        AIClient(load_settings().gemini_api_key)
    )
    translation_service = TranslationService()
    exporter = Exporter()

    while True:
        topic = request_topic()

        try:
            article = search_service.search(topic)
        except (requests.exceptions.RequestException, TimeoutError) as error:
            print(f"Error al buscar en Wikipedia: {error}")
            continue

        show_original_article(article)

        try:
            article = content_enhancer.enhance(article)
        except Exception as error:
            print(f"Error al enriquecer el artículo: {error}")
            return

        show_enriched_article(article)

        # Solicitar el idioma de destino.
        language_name, language_code = request_target_language()

        # Traducir el texto enriquecido por Gemini.
        try:
            translated_content = translation_service.translate(
                content=article.enriched,
                target_language=language_code,
                source_language="es",
            )
        except (
            requests.exceptions.RequestException,
            RuntimeError,
            ValueError,
        ) as error:
            print(f"Error al traducir el artículo: {error}")
            return

        print(f"\nARTÍCULO TRADUCIDO AL {language_name.upper()}")
        print("=" * 50)
        print(translated_content)

        # Preguntar si se desea guardar el resultado.
        file_format = request_export_format()

        try:
            file_path = exporter.export(
                title=f"{article.title}_{language_code}",
                content=translated_content,
                file_format=file_format,
            )
        except (OSError, ValueError) as error:
            print(f"Error al guardar el archivo: {error}")
            return

        print(f"\nArtículo guardado correctamente en: {file_path}")
        return


if __name__ == "__main__":
    main()
