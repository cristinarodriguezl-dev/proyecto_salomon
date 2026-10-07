"""Entry point of the application."""

from src.ui.topic_input import request_topic


def main() -> None:
    """Ask for a topic and show the answer from Wikipedia."""
    response = request_topic()
    print(f"Wikipedia responded with status {response.status_code}")


if __name__ == "__main__":
    main()
