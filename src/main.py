"""Coordina la búsqueda de Wikipedia y muestra el artículo original y el enriquecido."""

import requests

from src.ai.ai_client import AIClient
from src.ai.content_enhancer import ContentEnhancer
from src.exceptions import SearchError
from src.services.search_service import WikipediaSearchService
from src.settings import load_settings
from src.ui.article_display import show_enriched_article, show_original_article
from src.ui.search_continuation_prompt import SearchContinuationPrompt
from src.ui.topic_input import request_topic


def main() -> None:
    """Busca un artículo, lo muestra junto a su versión enriquecida y pregunta si repetir.

    Ante errores de red de Wikipedia, permite reintentar.
    """
    search_service = WikipediaSearchService()
    content_enhancer = ContentEnhancer(AIClient(load_settings().gemini_api_key))
    continuation_prompt = SearchContinuationPrompt()

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

        if not continuation_prompt.ask_search_again():
            print("Programa finalizado.")
            return


if __name__ == "__main__":
    main()
