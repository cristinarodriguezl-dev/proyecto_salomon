"""Pruebas del recorrido de traducción y presentación en terminal."""

from unittest.mock import call, patch

import pytest

from src.exceptions import EnrichmentError, TranslationError
from src.main import ORIGINAL_KEPT_MESSAGE, main
from src.settings import Settings
from src.models.article import Article
from src.ui.article_display import (
    EMPTY_TRANSLATED_MESSAGE,
    TRANSLATED_HEADER,
    show_translated_article,
)


@pytest.fixture
def flow_dependencies():
    article = Article(
        title="Árbol",
        paragraphs=["Primer original.", "Segundo original."],
    )
    with patch("src.main.WikipediaSearchService") as search_class, patch(
        "src.main.AIClient"
    ) as ai_class, patch("src.main.TranslationService") as translation_class, patch(
        "src.main.load_settings"
    ) as settings, patch("src.main.SummaryConfirmationPrompt") as summary_prompt_class:
        settings.return_value = Settings("fake-key", 10)
        summary_prompt_class.return_value.ask.return_value = False
        search_class.return_value.search.return_value = article
        ai_class.return_value.generate_text.return_value = (
            "Primero ampliado.\n\nSegundo ampliado."
        )
        service = translation_class.return_value
        service.get_supported_languages.return_value = {
            "en": "Inglés",
            "fr": "Francés",
            "es": "Español",
        }
        yield article, ai_class.return_value, service


def test_main_validates_language_translates_and_exports_saved_version(
    flow_dependencies, monkeypatch, tmp_path, capsys
) -> None:
    article, _ai_client, service = flow_dependencies
    service.translate.side_effect = ["First enriched.", "Second enriched."]
    answers = iter(["Árbol", "xx", "Inglés", "s", "3", "txt", "article", "2"])
    monkeypatch.setattr("builtins.input", lambda _message: next(answers))
    monkeypatch.chdir(tmp_path)

    main()

    assert article.translated == "First enriched.\n\nSecond enriched."
    assert article.enriched == "Primero ampliado.\n\nSegundo ampliado."
    assert service.translate.call_args_list == [
        call("Primero ampliado.", "en"),
        call("Segundo ampliado.", "en"),
    ]
    output = capsys.readouterr().out
    assert "Idioma no admitido" in output
    assert f"{TRANSLATED_HEADER} (Inglés)\n\n{article.translated}\n" in output
    assert article.translated in (tmp_path / "article.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("retry_language", "first", "second", "language_name"),
    [
        ("en", "First enriched.", "Second enriched.", "Inglés"),
        ("fr", "Premier enrichi.", "Deuxième enrichi.", "Francés"),
    ],
)
def test_main_retries_same_or_another_language_after_provider_failure(
    flow_dependencies, monkeypatch, capsys,
    retry_language, first, second, language_name,
) -> None:
    article, _ai_client, service = flow_dependencies
    service.translate.side_effect = [
        TranslationError("MyMemory no responde"),
        first,
        second,
    ]
    answers = iter(["Árbol", "en", retry_language, "n", "2"])
    monkeypatch.setattr("builtins.input", lambda _message: next(answers))

    main()

    output = capsys.readouterr().out
    assert "MyMemory no responde" in output
    assert output.count("¿A qué idioma quieres traducir el contenido?") == 2
    assert f"{TRANSLATED_HEADER} ({language_name})" in output
    assert article.translated == f"{first}\n\n{second}"
    assert service.translate.call_args_list == [
        call("Primero ampliado.", "en"),
        call("Primero ampliado.", retry_language),
        call("Segundo ampliado.", retry_language),
    ]


def test_main_can_skip_translation_after_provider_failure(
    flow_dependencies, monkeypatch, capsys
) -> None:
    article, _ai_client, service = flow_dependencies
    service.translate.side_effect = TranslationError("MyMemory no disponible")
    answers = iter(["Árbol", "en", "0", "n", "2"])
    monkeypatch.setattr("builtins.input", lambda _message: next(answers))

    main()

    output = capsys.readouterr().out
    assert "MyMemory no disponible" in output
    assert TRANSLATED_HEADER not in output
    assert output.endswith("Programa finalizado.\n")
    assert article.translated == ""


def test_main_translates_original_paragraphs_when_gemini_fails(
    flow_dependencies, monkeypatch, capsys
) -> None:
    article, ai_client, service = flow_dependencies
    ai_client.generate_text.side_effect = EnrichmentError("Gemini no disponible")
    service.translate.side_effect = ["First original.", "Second original."]
    answers = iter(["Árbol", "en", "n", "2"])
    monkeypatch.setattr("builtins.input", lambda _message: next(answers))

    main()

    output = capsys.readouterr().out
    assert f"Gemini no disponible\n{ORIGINAL_KEPT_MESSAGE}\n" in output
    assert article.enriched == ""
    assert article.translated == "First original.\n\nSecond original."
    assert service.translate.call_args_list == [
        call("Primer original.", "en"),
        call("Segundo original.", "en"),
    ]


def test_display_uses_saved_translation_and_separates_paragraphs(capsys) -> None:
    article = Article(
        title="Tema",
        paragraphs=["Original."],
        translated="First.\n\nSecond.",
    )

    show_translated_article(article, "Inglés")

    assert capsys.readouterr().out == (
        f"{TRANSLATED_HEADER} (Inglés)\n\nFirst.\n\nSecond.\n"
    )


def test_display_without_translation_reports_its_absence(capsys) -> None:
    article = Article(title="Tema", paragraphs=["Original."])

    show_translated_article(article, "Inglés")

    assert capsys.readouterr().out == f"{EMPTY_TRANSLATED_MESSAGE}\n"
