"""Pruebas de la selección del contenido que se exportará."""

import pytest

from src.models.article import Article
from src.ui.export_version_prompt import ExportVersionPrompt


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
        ("1", "Primer párrafo.\n\nSegundo párrafo."),
        ("2", "Texto enriquecido.\n\nOtro párrafo."),
        ("3", "Translated text."),
    ],
)
def test_each_choice_returns_the_selected_content(
    article, monkeypatch, choice, expected
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: choice)

    assert ExportVersionPrompt().ask(article) == expected
    assert article.paragraphs == ["Primer párrafo.", "Segundo párrafo."]
    assert article.enriched == "Texto enriquecido.\n\nOtro párrafo."
    assert article.translated == "Translated text."


def test_only_original_is_offered_when_other_versions_are_missing(
    monkeypatch, capsys
) -> None:
    article = Article(title="Árbol", paragraphs=["Texto original."])
    monkeypatch.setattr("builtins.input", lambda _: "1")

    assert ExportVersionPrompt().ask(article) == "Texto original."
    output = capsys.readouterr().out
    assert "1. Original" in output
    assert "2. Enriquecida" not in output
    assert "3. Traducida" not in output


def test_translation_is_offered_even_without_enrichment(monkeypatch, capsys) -> None:
    article = Article(
        title="Árbol", paragraphs=["Original."], translated="Translation."
    )
    monkeypatch.setattr("builtins.input", lambda _: "3")

    assert ExportVersionPrompt().ask(article) == "Translation."
    output = capsys.readouterr().out
    assert "2. Enriquecida" not in output
    assert "3. Traducida" in output


def test_unavailable_choice_is_explained_and_can_be_corrected(
    monkeypatch, capsys
) -> None:
    article = Article(title="Árbol", paragraphs=["Original."])
    choices = iter(["2", " 1 "])
    monkeypatch.setattr("builtins.input", lambda _: next(choices))

    assert ExportVersionPrompt().ask(article) == "Original."
    assert "Esa versión no está disponible" in capsys.readouterr().out


def test_blank_version_is_not_offered(monkeypatch, capsys) -> None:
    article = Article(
        title="Árbol", paragraphs=["Original."], enriched="   ", translated="\n"
    )
    monkeypatch.setattr("builtins.input", lambda _: "1")

    assert ExportVersionPrompt().ask(article) == "Original."
    output = capsys.readouterr().out
    assert "2. Enriquecida" not in output
    assert "3. Traducida" not in output
