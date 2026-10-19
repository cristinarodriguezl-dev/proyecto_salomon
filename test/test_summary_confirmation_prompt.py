"""Tests de SummaryConfirmationPrompt."""

from types import SimpleNamespace

import questionary

from src.ui.summary_confirmation_prompt import (
    NO_OPTION,
    OPTIONS,
    PROMPT_MESSAGE,
    YES_OPTION,
    SummaryConfirmationPrompt,
)


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


def test_ask_returns_true_when_the_answer_is_yes(monkeypatch) -> None:
    install_questionary(monkeypatch, [YES_OPTION])

    assert SummaryConfirmationPrompt().ask() is True


def test_ask_returns_false_when_the_answer_is_no(monkeypatch) -> None:
    install_questionary(monkeypatch, [NO_OPTION])

    assert SummaryConfirmationPrompt().ask() is False


def test_ask_offers_exactly_the_yes_and_no_options(monkeypatch) -> None:
    prompts = install_questionary(monkeypatch, [YES_OPTION])

    SummaryConfirmationPrompt().ask()

    assert prompts.messages == [PROMPT_MESSAGE]
    assert prompts.choices == [OPTIONS]
