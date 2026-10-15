"""Coordina la búsqueda, la presentación y la exportación del artículo."""

import requests

from src.ai.ai_client import AIClient
from src.ai.content_enhancer import ContentEnhancer
from src.exceptions import ExportError, SearchError
from src.export.export_service import ExportService
from src.services.search_service import WikipediaSearchService
from src.settings import load_settings
from src.ui.article_display import show_enriched_article, show_original_article
from src.ui.export_confirmation_prompt import ExportConfirmationPrompt
from src.ui.export_destination_prompt import ExportDestinationPrompt
from src.ui.export_version_prompt import ExportVersionPrompt
from src.ui.search_continuation_prompt import SearchContinuationPrompt
from src.ui.topic_input import request_topic


def main() -> None:
    """Busca, muestra y ofrece guardar el artículo antes de repetir o salir.

    Ante errores de red de Wikipedia, permite reintentar.
    """
    search_service = WikipediaSearchService()
    content_enhancer = ContentEnhancer(AIClient(load_settings().gemini_api_key))
    continuation_prompt = SearchContinuationPrompt()
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
        article = content_enhancer.enhance(article)
        show_enriched_article(article)

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
