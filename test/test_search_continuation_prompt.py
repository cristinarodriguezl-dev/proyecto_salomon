"""Tests de SearchContinuationPrompt."""

from src.ui.search_continuation_prompt import SearchContinuationPrompt


def test_ask_search_again_returns_true_when_option_is_one(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")

    assert SearchContinuationPrompt().ask_search_again() is True


def test_ask_search_again_returns_false_when_option_is_two(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "2")

    assert SearchContinuationPrompt().ask_search_again() is False


def test_ask_search_again_ignores_surrounding_spaces(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: " 2 ")

    assert SearchContinuationPrompt().ask_search_again() is False


def test_ask_search_again_repeats_until_option_is_valid(monkeypatch, capsys):
    answers = iter(["", "abc", "3", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = SearchContinuationPrompt().ask_search_again()

    assert result is True
    assert capsys.readouterr().out.count("Opción no válida") == 3