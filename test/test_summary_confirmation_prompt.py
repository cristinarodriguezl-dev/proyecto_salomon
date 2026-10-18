"""Tests de SummaryConfirmationPrompt."""

from src.ui.summary_confirmation_prompt import SummaryConfirmationPrompt


def test_ask_returns_true_when_the_answer_is_yes(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "s")

    assert SummaryConfirmationPrompt().ask() is True


def test_ask_accepts_si_with_accent_and_surrounding_spaces(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: " Sí ")

    assert SummaryConfirmationPrompt().ask() is True


def test_ask_returns_false_when_the_answer_is_no(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "n")

    assert SummaryConfirmationPrompt().ask() is False


def test_ask_repeats_until_the_answer_is_valid(monkeypatch, capsys) -> None:
    answers = iter(["", "quizá", "no"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = SummaryConfirmationPrompt().ask()

    assert result is False
    assert capsys.readouterr().out.count("Respuesta no válida") == 2