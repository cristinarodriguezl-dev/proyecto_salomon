"""Terminal input for selecting a Wikipedia search topic."""

PROMPT_MESSAGE = "Enter the topic to search in Wikipedia: "
EMPTY_INPUT_MESSAGE = "The topic cannot be empty. Try again."


def request_topic() -> str:
    """Ask until a non-empty topic is entered and return it without outer spaces."""
    while True:
        topic = input(PROMPT_MESSAGE).strip()

        if topic:
            return topic

        print(EMPTY_INPUT_MESSAGE)
