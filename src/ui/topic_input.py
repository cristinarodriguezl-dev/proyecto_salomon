"""Terminal input that requests a topic and searches Wikipedia."""

import requests

from src.scraping.wikipedia_client import WikipediaClient

PROMPT_MESSAGE = "Enter the topic to search in Wikipedia: "
EMPTY_INPUT_MESSAGE = "The topic cannot be empty. Try again."


def request_topic() -> requests.Response:
    """Ask for a topic until it is valid and search Wikipedia with it."""
    while True:
        topic = input(PROMPT_MESSAGE).strip()

        if topic:
            return WikipediaClient().fetch(topic)

        print(EMPTY_INPUT_MESSAGE)
