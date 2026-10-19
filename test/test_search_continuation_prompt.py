"""Tests de SearchContinuationPrompt."""

from types import SimpleNamespace

import questionary

from src.ui.search_continuation_prompt import SearchContinuationPrompt


def install_questionary(monkeypatch, answers):
    """Sustituye las preguntas de questionary por respuestas fijas."""
    pending = iter(answers)
    prompts = SimpleNamespace(messages=[], choices=[])

    def question(message, *args, **kwargs):
        prompts.messages.append(message)
        prompts.choices.append(kwargs.get("choices"))
        return SimpleNamespace(unsafe_ask=lambda: next(pending))

    for name in ("text", "select", "confirm"):
        monkeypatch.setattr(questionary, name, question)

    return prompts


def test_ask_search_again_returns_true_when_the_search_again_option_is_selected(
    monkeypatch,
):
    install_questionary(
        monkeypatch, [SearchContinuationPrompt.SEARCH_AGAIN_OPTION]
    )

    assert SearchContinuationPrompt().ask_search_again() is True


def test_ask_search_again_returns_false_when_the_exit_option_is_selected(
    monkeypatch,
):
    install_questionary(monkeypatch, [SearchContinuationPrompt.EXIT_OPTION])

    assert SearchContinuationPrompt().ask_search_again() is False


def test_ask_search_again_offers_the_menu_options(monkeypatch):
    prompts = install_questionary(
        monkeypatch, [SearchContinuationPrompt.SEARCH_AGAIN_OPTION]
    )

    SearchContinuationPrompt().ask_search_again()

    assert prompts.messages == [SearchContinuationPrompt.MENU_MESSAGE]
    assert prompts.choices == [SearchContinuationPrompt.OPTIONS]
    assert SearchContinuationPrompt.OPTIONS == [
        SearchContinuationPrompt.SEARCH_AGAIN_OPTION,
        SearchContinuationPrompt.EXIT_OPTION,
    ]
