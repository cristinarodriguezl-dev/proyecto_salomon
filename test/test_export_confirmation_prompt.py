"""Comprueba que una respuesta inválida permite confirmar o rechazar el guardado."""

from unittest.mock import Mock

import pytest

from src.ui.export_confirmation_prompt import ExportConfirmationPrompt


@pytest.mark.parametrize(("answer", "expected"), [("sí", True), ("no", False)])
def test_invalid_answer_is_retried_before_returning_the_save_decision(
    answer, expected, monkeypatch, capsys
):
    read_answer = Mock(side_effect=["quizás", answer])
    monkeypatch.setattr("builtins.input", read_answer)

    assert ExportConfirmationPrompt().ask() is expected

    assert read_answer.call_count == 2
    assert capsys.readouterr().out == "Respuesta no válida. Escribe s o n.\n"
