"""Pruebas del recorrido principal cuando la traducción no se puede completar."""

from unittest.mock import patch

import pytest
import requests

from src.main import main
from src.models.article import Article
from src.translation.translation_service import (
    CONNECTION_ERROR_MESSAGE,
    SERVICE_ERROR_MESSAGE,
)

ENRICHED_TEXT = "Texto enriquecido por IA."
LANGUAGE_MENU_OPTION = "0 - Omitir traducción"
EXIT_OUTPUT = "Programa finalizado.\n"


@pytest.fixture
def main_dependencies():
    """Sustituye Wikipedia y Gemini; el servicio de traducción es el real."""
    article = Article(title="Árbol", paragraphs=["Primer párrafo."])
    with patch("src.main.WikipediaSearchService") as search_class, patch(
        "src.main.AIClient"
    ) as ai_class, patch("src.main.load_settings") as settings, patch(
        "src.main.SummaryConfirmationPrompt"
    ) as summary_prompt_class:
        search_class.return_value.search.return_value = article
        ai_class.return_value.generate_text.return_value = ENRICHED_TEXT
        settings.return_value.gemini_api_key = "fake_key"
        summary_prompt_class.return_value.ask.return_value = False
        yield


def run_main(monkeypatch, answers) -> None:
    pending_answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _message: next(pending_answers))
    main()


@pytest.mark.parametrize(
    ("network_error", "expected_message"),
    [
        (requests.exceptions.ConnectionError("sin red"), CONNECTION_ERROR_MESSAGE),
        (requests.exceptions.HTTPError("503"), SERVICE_ERROR_MESSAGE),
    ],
    ids=["connection_failure", "service_failure"],
)
def test_main_explains_the_failure_and_lets_the_user_continue(
    network_error, expected_message, main_dependencies, monkeypatch, capsys
) -> None:
    with patch("src.translation.translation_service.requests.get") as get:
        get.side_effect = network_error

        run_main(monkeypatch, ["Árbol", "en", "0", "n", "2"])

    output = capsys.readouterr().out
    assert f"{expected_message}\n" in output
    assert output.count(LANGUAGE_MENU_OPTION) == 2
    assert output.endswith(EXIT_OUTPUT)


def test_main_reports_an_unsupported_language_without_calling_the_service(
    main_dependencies, monkeypatch, capsys
) -> None:
    with patch("src.translation.translation_service.requests.get") as get:
        run_main(monkeypatch, ["Árbol", "klingon", "0", "n", "2"])

    output = capsys.readouterr().out
    assert "Idioma no admitido." in output
    assert CONNECTION_ERROR_MESSAGE not in output
    assert SERVICE_ERROR_MESSAGE not in output
    assert output.endswith(EXIT_OUTPUT)
    get.assert_not_called()