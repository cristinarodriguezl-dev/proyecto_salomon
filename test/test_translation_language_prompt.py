"""Pruebas de la selección de idioma de destino."""

from unittest.mock import Mock

import pytest

from src.translation.translation_service import TranslationService
from src.ui.translation_language_prompt import TranslationLanguagePrompt


@pytest.fixture
def prompt() -> TranslationLanguagePrompt:
    service = Mock(spec=TranslationService)
    service.get_supported_languages.return_value = {
        "en": "Inglés",
        "fr": "Francés",
    }
    return TranslationLanguagePrompt(service)


@pytest.mark.parametrize(
    "answer", ["en", " INGLÉS ", "FrAnCéS", "fr"]
)
def test_accepts_supported_code_or_name(answer, prompt, monkeypatch, capsys) -> None:
    monkeypatch.setattr("builtins.input", lambda _message: answer)

    result = prompt.ask()

    assert result == ("fr" if answer.casefold().strip() in {"fr", "francés"} else "en")
    output = capsys.readouterr().out
    assert "en - Inglés" in output
    assert "fr - Francés" in output


def test_reprompts_after_unsupported_language(prompt, monkeypatch, capsys) -> None:
    answers = iter(["xx", "", "fr"])
    monkeypatch.setattr("builtins.input", lambda _message: next(answers))

    assert prompt.ask() == "fr"
    assert capsys.readouterr().out.count("Idioma no admitido") == 2


def test_can_skip_translation(prompt, monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _message: "0")

    assert prompt.ask() is None
