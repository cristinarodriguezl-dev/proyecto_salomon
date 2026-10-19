"""Integration tests: a Gemini failure must not lose the Wikipedia article."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
import questionary
import requests

from src.ai.ai_client import (
    INVALID_API_KEY_MESSAGE,
    NETWORK_ERROR_MESSAGE,
    RATE_LIMIT_MESSAGE,
    SERVICE_ERROR_MESSAGE,
    TIMEOUT_MESSAGE,
)
from src.exceptions import EnrichmentError
from src.main import ORIGINAL_KEPT_MESSAGE, main
from src.scraping.wikipedia_client import WIKIPEDIA_SEARCH_URL
from src.ui.article_display import ENRICHED_HEADER
from src.ui.export_destination_prompt import EXPORT_DIRECTORY
from src.ui.article_display import ENRICHED_HEADER, ORIGINAL_HEADER, SEPARATOR

ARTICLE_RESPONSE = requests.Response()
ARTICLE_RESPONSE.status_code = 200
ARTICLE_RESPONSE.url = WIKIPEDIA_SEARCH_URL
ARTICLE_RESPONSE._content = (
    '<h1 id="firstHeading">Árbol</h1>'
    '<div id="mw-content-text"><div class="mw-parser-output">'
    "<p>Primer párrafo.</p></div></div>"
).encode("utf-8")


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



@pytest.mark.parametrize(
    "expected_message",
    [
        INVALID_API_KEY_MESSAGE,
        TIMEOUT_MESSAGE,
        NETWORK_ERROR_MESSAGE,
        RATE_LIMIT_MESSAGE,
        SERVICE_ERROR_MESSAGE,
    ],
)
def test_main_keeps_original_article_when_gemini_fails(
    expected_message, monkeypatch, capsys
):
    install_questionary(monkeypatch, ["Árbol", "No", "Salir"])

    with patch("src.main.AIClient") as ai_client_class, patch(
        "src.scraping.wikipedia_client.requests.get", return_value=ARTICLE_RESPONSE
    ), patch("src.main.TranslationLanguagePrompt") as language_prompt_class, patch(
        "src.main.SummaryConfirmationPrompt"
    ) as summary_prompt_class:
        language_prompt_class.return_value.ask.return_value = None
        summary_prompt_class.return_value.ask.return_value = False
        ai_client_class.return_value.generate_text.side_effect = EnrichmentError(
            expected_message
        )
        main()

    output = capsys.readouterr().out
    assert (
        f"Árbol\n=====\n\n{ORIGINAL_HEADER}\n\nPrimer párrafo.\n\n{SEPARATOR}\n\n"
        in output
    )
    assert f"{expected_message}\n{ORIGINAL_KEPT_MESSAGE}\n" in output
    assert ENRICHED_HEADER not in output
    assert output.endswith("Programa finalizado.\n")


def test_main_can_export_original_after_gemini_failure(
    monkeypatch, tmp_path, capsys
):
    monkeypatch.chdir(tmp_path)
    install_questionary(
        monkeypatch, ["Árbol", "Sí", "Original", "TXT", "articulo", "Salir"]
    )

    with patch("src.main.AIClient") as ai_client_class, patch(
        "src.scraping.wikipedia_client.requests.get", return_value=ARTICLE_RESPONSE
    ), patch("src.main.TranslationLanguagePrompt") as language_prompt_class, patch(
        "src.main.SummaryConfirmationPrompt"
    ) as summary_prompt_class:
        language_prompt_class.return_value.ask.return_value = None
        summary_prompt_class.return_value.ask.return_value = False
        ai_client_class.return_value.generate_text.side_effect = EnrichmentError(
            SERVICE_ERROR_MESSAGE
        )
        main()

    assert (tmp_path / EXPORT_DIRECTORY / "articulo.txt").read_text(
        encoding="utf-8"
    ) == (
        "Árbol\n=====\n\nPrimer párrafo.\n"
    )
    output = capsys.readouterr().out
    assert f"{SERVICE_ERROR_MESSAGE}\n{ORIGINAL_KEPT_MESSAGE}\n" in output
    assert f"Archivo guardado: {EXPORT_DIRECTORY / 'articulo.txt'}" in output
    assert ENRICHED_HEADER not in output
    assert output.endswith("Programa finalizado.\n")