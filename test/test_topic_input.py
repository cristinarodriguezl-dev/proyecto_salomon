"""Pruebas de solicitud y validación del tema de búsqueda."""

from types import SimpleNamespace

import questionary

from src.ui.topic_input import EMPTY_INPUT_MESSAGE, PROMPT_MESSAGE, request_topic


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


def test_request_topic_repeats_empty_input_and_returns_trimmed_topic(
    monkeypatch, capsys
) -> None:
    prompts = install_questionary(monkeypatch, ["   ", "  Árbol  "])

    topic = request_topic()

    assert topic == "Árbol"
    assert prompts.messages == [PROMPT_MESSAGE, PROMPT_MESSAGE]
    assert capsys.readouterr().out == f"{EMPTY_INPUT_MESSAGE}\n"


def test_request_topic_returns_valid_input_without_error_message(
    monkeypatch, capsys
) -> None:
    install_questionary(monkeypatch, ["  Historia  "])

    topic = request_topic()

    assert topic == "Historia"
    assert capsys.readouterr().out == ""
