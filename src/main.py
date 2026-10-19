"""Coordina búsqueda, resumen, traducción, presentación y exportación del artículo."""

import requests

from src.ai.ai_client import AIClient
from src.ai.content_enhancer import ContentEnhancer
from src.ai.content_summarizer import ContentSummarizer
from src.exceptions import EnrichmentError, ExportError, SearchError, TranslationError
from src.export.export_service import ExportService
from src.scraping.wikipedia_client import WikipediaClient
from src.services.search_service import WikipediaSearchService
from src.settings import load_settings
from src.translation.article_translator import ArticleTranslator
from src.translation.translation_service import TranslationService
from src.ui.article_display import (
    show_enriched_article,
    show_original_article,
    show_translated_article,
)
from src.ui.export_confirmation_prompt import ExportConfirmationPrompt
from src.ui.export_destination_prompt import ExportDestinationPrompt
from src.ui.export_version_prompt import ExportVersionPrompt
from src.ui.search_continuation_prompt import SearchContinuationPrompt
from src.ui.summary_confirmation_prompt import SummaryConfirmationPrompt
from src.ui.summary_display import show_summary
from src.ui.topic_input import request_topic
from src.ui.translation_language_prompt import TranslationLanguagePrompt

ORIGINAL_KEPT_MESSAGE = "Se mantiene el artículo original de Wikipedia."


def main() -> None:
    """Busca, muestra, resume, traduce y ofrece guardar antes de repetir o salir.

    Ante errores de red de Wikipedia, permite reintentar.
    """
    try:
        settings = load_settings()
    except ValueError as error:
        print(f"Error de configuración: {error}")
        return

    search_service = WikipediaSearchService(
        wikipedia_client=WikipediaClient(timeout_seconds=settings.wikipedia_timeout)
    )
    ai_client = AIClient(settings.gemini_api_key)
    content_enhancer = ContentEnhancer(ai_client)
    content_summarizer = ContentSummarizer(ai_client)
    summary_confirmation_prompt = SummaryConfirmationPrompt()
    continuation_prompt = SearchContinuationPrompt()
    translation_service = TranslationService()
    translation_language_prompt = TranslationLanguagePrompt(translation_service)
    article_translator = ArticleTranslator(translation_service)
    export_confirmation_prompt = ExportConfirmationPrompt()
    export_version_prompt = ExportVersionPrompt()
    export_destination_prompt = ExportDestinationPrompt()
    export_service = ExportService()

    while True:
        topic = request_topic()

        try:
            article = search_service.search(topic)
        except (
            requests.exceptions.RequestException,
            TimeoutError,
            SearchError,
        ) as error:
            print(error)
            continue

        show_original_article(article)
        try:
            article = content_enhancer.enhance(article)
        except EnrichmentError as error:
            print(error)
            print(ORIGINAL_KEPT_MESSAGE)
        else:
            show_enriched_article(article)

        if summary_confirmation_prompt.ask():
            try:
                article = content_summarizer.summarize(article)
            except EnrichmentError as error:
                print(error)
            else:
                show_summary(article)

        while True:
            target_language = translation_language_prompt.ask()
            if target_language is None:
                break

            try:
                article = article_translator.translate(article, target_language)
            except (TranslationError, ValueError) as error:
                print(error)
                continue

            language_name = translation_service.get_supported_languages()[target_language]
            show_translated_article(article, language_name)
            break

        if export_confirmation_prompt.ask():
            content = export_version_prompt.ask(article)
            destination = export_destination_prompt.ask()
            try:
                export_service.export(article.title, content, destination)
            except ExportError as error:
                print(error)
            else:
                print(f"Archivo guardado: {destination.path}")

        if not continuation_prompt.ask_search_again():
            print("Programa finalizado.")
            return


if __name__ == "__main__":
    main()
