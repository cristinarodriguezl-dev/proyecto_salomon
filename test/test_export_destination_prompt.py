"""Pruebas de la selección del formato y destino de exportación."""

from types import SimpleNamespace

import pytest
import questionary

from src.ui.export_destination_prompt import (
    EMPTY_NAME_MESSAGE,
    EXPORT_DIRECTORY,
    FORMAT_PROMPT,
    INVALID_NAME_MESSAGE,
    NAME_PROMPT,
    WRONG_EXTENSION_MESSAGE,
    ExportDestination,
    ExportDestinationPrompt,
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


@pytest.mark.parametrize(
    ("answers", "expected"),
    [
        (["TXT", " informe "], ExportDestination("txt", EXPORT_DIRECTORY / "informe.txt")),
        (["PDF", "informe.PDF"], ExportDestination("pdf", EXPORT_DIRECTORY / "informe.pdf")),
    ],
)
def test_ask_returns_the_selected_format_and_destination(
    answers, expected, monkeypatch, tmp_path, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    prompts = install_questionary(monkeypatch, answers)

    result = ExportDestinationPrompt().ask()

    assert result == expected
    assert prompts.messages == [FORMAT_PROMPT, NAME_PROMPT]
    assert prompts.choices[0] == ["TXT", "PDF"]
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    ("invalid_name", "message"),
    [
        ("   ", EMPTY_NAME_MESSAGE),
        ("../informe", INVALID_NAME_MESSAGE),
        ("../informe.pdf", INVALID_NAME_MESSAGE),
        ("carpeta\\informe", INVALID_NAME_MESSAGE),
        (".txt", INVALID_NAME_MESSAGE),
        ("informe?", INVALID_NAME_MESSAGE),
        ("CON", INVALID_NAME_MESSAGE),
        ("informe.", INVALID_NAME_MESSAGE),
        ("a" * 252, INVALID_NAME_MESSAGE),
        ("informe.pdf", WRONG_EXTENSION_MESSAGE),
    ],
)
def test_ask_repeats_an_invalid_name_and_allows_correction(
    invalid_name, message, monkeypatch, tmp_path, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    prompts = install_questionary(monkeypatch, ["TXT", invalid_name, "informe.txt"])

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("txt", EXPORT_DIRECTORY / "informe.txt")
    assert prompts.messages == [FORMAT_PROMPT, NAME_PROMPT, NAME_PROMPT]
    assert capsys.readouterr().out == f"{message}\n"
