"""Coordina la búsqueda de Wikipedia y muestra el artículo original."""

import requests

from src.services.search_service import WikipediaSearchService
from src.ui.article_display import show_original_article
from src.ui.search_continuation_prompt import SearchContinuationPrompt
from src.ui.topic_input import request_topic


def main() -> None:
    """Busca y muestra un artículo; ante errores de red, permite reintentar."""
    search_service = WikipediaSearchService()
    continuation_prompt = SearchContinuationPrompt()


    while True:
        topic = request_topic()

        try:
            article = search_service.search(topic)
        except (requests.exceptions.RequestException, TimeoutError) as error:
            print(error)
            continue

        show_original_article(article)

        if not continuation_prompt.ask_search_again():
            print("Programa finalizado.")
            return


if __name__ == "__main__":
    main()