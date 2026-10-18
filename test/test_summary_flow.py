"""Pruebas del recorrido principal con la opción de resumir el contenido."""

from unittest.mock import patch

import pytest

from src.ai.content_summarizer import NO_ENRICHED_CONTENT_MESSAGE
from src.exceptions import EnrichmentError
from src.main import ORIGINAL_KEPT_MESSAGE, main
from src.models.article import Article
from src.ui.article_display import ENRICHED_HEADER
from src.ui.summary_display import SUMMARY_HEADER

ENRICHED_TEXT = "Texto enriquecido por IA."
SUMMARY_TEXT = "Resumen generado por IA."


@pytest.fixture
def flow_dependencies():
    """Sustituye Wikipedia, Gemini y la traducción para probar sin red."""
    article = Article(title="Árbol", paragraphs=["Primer párrafo."])
    with patch("src.main.WikipediaSearchService") as search_class, patch(
        "src.main.AIClient"
    ) as ai_class, patch("src.main.TranslationLanguagePrompt") as language_class, patch(
        "src.main.SummaryConfirmationPrompt"
    ) as summary_prompt_class:
        search_class.return_value.search.return_value = article
        language_class.return_value.ask.return_value = None
        yield ai_class.return_value, summary_prompt_class.return_value


def run_main(monkeypatch) -> None:
    answers = iter(["Árbol", "n", "2"])
    monkeypatch.setattr("builtins.input", lambda _message: next(answers))
    main()


def test_main_shows_the_summary_when_the_user_accepts(
    flow_dependencies, monkeypatch, capsys
) -> None:
    ai_client, summary_prompt = flow_dependencies
    ai_client.generate_text.side_effect = [ENRICHED_TEXT, SUMMARY_TEXT]
    summary_prompt.ask.return_value = True

    run_main(monkeypatch)

    output = capsys.readouterr().out
    assert f"{ENRICHED_HEADER}\n\n{ENRICHED_TEXT}\n" in output
    assert f"{SUMMARY_HEADER}\n\n{SUMMARY_TEXT}\n" in output
    assert output.endswith("Programa finalizado.\n")


def test_main_does_not_summarize_when_the_user_declines(
    flow_dependencies, monkeypatch, capsys
) -> None:
    ai_client, summary_prompt = flow_dependencies
    ai_client.generate_text.return_value = ENRICHED_TEXT
    summary_prompt.ask.return_value = False

    run_main(monkeypatch)

    assert SUMMARY_HEADER not in capsys.readouterr().out
    ai_client.generate_text.assert_called_once()


def test_main_explains_what_is_missing_when_there_is_no_enriched_content(
    flow_dependencies, monkeypatch, capsys
) -> None:
    ai_client, summary_prompt = flow_dependencies
    ai_client.generate_text.side_effect = EnrichmentError("Gemini no disponible")
    summary_prompt.ask.return_value = True

    run_main(monkeypatch)

    output = capsys.readouterr().out
    assert f"Gemini no disponible\n{ORIGINAL_KEPT_MESSAGE}\n" in output
    assert f"{NO_ENRICHED_CONTENT_MESSAGE}\n" in output
    assert SUMMARY_HEADER not in output
    assert output.endswith("Programa finalizado.\n")


def test_main_reports_a_summary_failure_and_keeps_going(
    flow_dependencies, monkeypatch, capsys
) -> None:
    ai_client, summary_prompt = flow_dependencies
    ai_client.generate_text.side_effect = [
        ENRICHED_TEXT,
        EnrichmentError("Gemini falló al resumir"),
    ]
    summary_prompt.ask.return_value = True

    run_main(monkeypatch)

    output = capsys.readouterr().out
    assert "Gemini falló al resumir\n" in output
    assert SUMMARY_HEADER not in output
    assert output.endswith("Programa finalizado.\n")