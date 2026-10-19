"""Pruebas de la selección de idioma de destino."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import questionary

from src.translation.translation_service import TranslationService
from src.ui.translation_language_prompt import TranslationLanguagePrompt


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


@pytest.fixture
def prompt() -> TranslationLanguagePrompt:
    service = Mock(spec=TranslationService)
    service.get_supported_languages.return_value = {
        "en": "Inglés",
        "fr": "Francés",
    }
    return TranslationLanguagePrompt(service)


def test_offers_every_supported_language_and_returns_the_selected_code(
    prompt, monkeypatch
) -> None:
    prompts = install_questionary(monkeypatch, ["fr"])

    result = prompt.ask()

    assert result == "fr"
    assert prompts.messages == [TranslationLanguagePrompt.MENU_MESSAGE]
    assert [choice.title for choice in prompts.choices[0]] == [
        "en - Inglés",
        "fr - Francés",
        TranslationLanguagePrompt.SKIP_LABEL,
    ]
    assert [choice.value for choice in prompts.choices[0]] == [
        "en",
        "fr",
        TranslationLanguagePrompt.SKIP_LABEL,
    ]


@pytest.mark.parametrize("code", ["en", "fr"])
def test_returns_the_code_of_each_offered_language(code, prompt, monkeypatch) -> None:
    install_questionary(monkeypatch, [code])

    assert prompt.ask() == code


def test_can_skip_translation(prompt, monkeypatch) -> None:
    install_questionary(monkeypatch, [TranslationLanguagePrompt.SKIP_LABEL])

    assert prompt.ask() is None
