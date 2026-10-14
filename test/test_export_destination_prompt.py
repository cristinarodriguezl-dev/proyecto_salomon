"""Pruebas de la selección del formato y destino de exportación."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.ui.export_destination_prompt import (
    EMPTY_NAME_MESSAGE,
    FORMAT_PROMPT,
    INVALID_FORMAT_MESSAGE,
    INVALID_NAME_MESSAGE,
    NAME_PROMPT,
    WRONG_EXTENSION_MESSAGE,
    ExportDestination,
    ExportDestinationPrompt,
)


@pytest.mark.parametrize(
    ("answers", "expected"),
    [
        ([" TXT ", " informe "], ExportDestination("txt", Path("informe.txt"))),
        (["pdf", "informe.PDF"], ExportDestination("pdf", Path("informe.pdf"))),
    ],
)
def test_ask_returns_the_selected_format_and_destination(
    answers, expected, monkeypatch, capsys
) -> None:
    fake_input = Mock(side_effect=answers)
    monkeypatch.setattr("builtins.input", fake_input)

    result = ExportDestinationPrompt().ask()

    assert result == expected
    assert [call.args[0] for call in fake_input.call_args_list] == [
        FORMAT_PROMPT,
        NAME_PROMPT,
    ]
    assert capsys.readouterr().out == ""


def test_ask_repeats_an_empty_or_unsupported_format(monkeypatch, capsys) -> None:
    fake_input = Mock(side_effect=["  ", "docx", " PDF ", "informe"])
    monkeypatch.setattr("builtins.input", fake_input)

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("pdf", Path("informe.pdf"))
    assert [call.args[0] for call in fake_input.call_args_list] == [
        FORMAT_PROMPT,
        FORMAT_PROMPT,
        FORMAT_PROMPT,
        NAME_PROMPT,
    ]
    assert capsys.readouterr().out == f"{INVALID_FORMAT_MESSAGE}\n" * 2


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
    invalid_name, message, monkeypatch, capsys
) -> None:
    fake_input = Mock(side_effect=["txt", invalid_name, "informe.txt"])
    monkeypatch.setattr("builtins.input", fake_input)

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("txt", Path("informe.txt"))
    assert [call.args[0] for call in fake_input.call_args_list] == [
        FORMAT_PROMPT,
        NAME_PROMPT,
        NAME_PROMPT,
    ]
    assert capsys.readouterr().out == f"{message}\n"
