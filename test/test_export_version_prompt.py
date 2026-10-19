"""Pruebas de la selección del contenido que se exportará."""

from types import SimpleNamespace

import pytest
import questionary

from src.models.article import Article
from src.ui.export_version_prompt import ExportVersionPrompt


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
def article() -> Article:
    return Article(
        title="Árbol",
        paragraphs=["Primer párrafo.", "Segundo párrafo."],
        enriched="Texto enriquecido.\n\nOtro párrafo.",
        translated="Translated text.",
    )


@pytest.mark.parametrize(
    ("choice", "expected"),
    [
        ("Original", "Primer párrafo.\n\nSegundo párrafo."),
        ("Enriquecida", "Texto enriquecido.\n\nOtro párrafo."),
        ("Traducida", "Translated text."),
    ],
)
def test_each_choice_returns_the_selected_content(
    article, monkeypatch, choice, expected
) -> None:
    install_questionary(monkeypatch, [choice])

    assert ExportVersionPrompt().ask(article) == expected
    assert article.paragraphs == ["Primer párrafo.", "Segundo párrafo."]
    assert article.enriched == "Texto enriquecido.\n\nOtro párrafo."
    assert article.translated == "Translated text."


def test_only_original_is_offered_when_other_versions_are_missing(
    monkeypatch
) -> None:
    article = Article(title="Árbol", paragraphs=["Texto original."])
    prompts = install_questionary(monkeypatch, ["Original"])

    assert ExportVersionPrompt().ask(article) == "Texto original."
    assert prompts.messages == [ExportVersionPrompt.MENU_MESSAGE]
    assert prompts.choices == [["Original"]]


def test_translation_is_offered_even_without_enrichment(monkeypatch) -> None:
    article = Article(
        title="Árbol", paragraphs=["Original."], translated="Translation."
    )
    prompts = install_questionary(monkeypatch, ["Traducida"])

    assert ExportVersionPrompt().ask(article) == "Translation."
    assert prompts.choices == [["Original", "Traducida"]]


def test_blank_version_is_not_offered(monkeypatch) -> None:
    article = Article(
        title="Árbol", paragraphs=["Original."], enriched="   ", translated="\n"
    )
    prompts = install_questionary(monkeypatch, ["Original"])

    assert ExportVersionPrompt().ask(article) == "Original."
    assert prompts.choices == [["Original"]]
