"""Pruebas de solicitud y validación del tema de búsqueda."""

from src.ui.topic_input import EMPTY_INPUT_MESSAGE, PROMPT_MESSAGE, request_topic


def test_request_topic_repeats_empty_input_and_returns_trimmed_topic(
    monkeypatch, capsys
) -> None:
    answers = iter(["   ", "  Árbol  "])
    prompts: list[str] = []

    def fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)

    topic = request_topic()

    assert topic == "Árbol"
    assert prompts == [PROMPT_MESSAGE, PROMPT_MESSAGE]
    assert capsys.readouterr().out == f"{EMPTY_INPUT_MESSAGE}\n"


def test_request_topic_returns_valid_input_without_error_message(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt: "  Historia  ")

    topic = request_topic()

    assert topic == "Historia"
    assert capsys.readouterr().out == ""
