"""Integration tests: a Gemini failure must not lose the Wikipedia article."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.ai.ai_client import (
    INVALID_API_KEY_MESSAGE,
    RATE_LIMIT_MESSAGE,
    SERVICE_ERROR_MESSAGE,
    TIMEOUT_MESSAGE,
)
from src.exceptions import EnrichmentError
from src.main import ORIGINAL_KEPT_MESSAGE, main
from src.scraping.wikipedia_client import WIKIPEDIA_SEARCH_URL
from src.ui.article_display import ENRICHED_HEADER

ARTICLE_RESPONSE = requests.Response()
ARTICLE_RESPONSE.status_code = 200
ARTICLE_RESPONSE.url = WIKIPEDIA_SEARCH_URL
ARTICLE_RESPONSE._content = (
    '<h1 id="firstHeading">Árbol</h1>'
    '<div id="mw-content-text"><div class="mw-parser-output">'
    "<p>Primer párrafo.</p></div></div>"
).encode("utf-8")


@pytest.mark.parametrize(
    "expected_message",
    [
        INVALID_API_KEY_MESSAGE,
        TIMEOUT_MESSAGE,
        RATE_LIMIT_MESSAGE,
        SERVICE_ERROR_MESSAGE,
    ],
)
def test_main_keeps_original_article_when_gemini_fails(
    expected_message, monkeypatch, capsys
):
    answers = iter(["Árbol", "2"])
    monkeypatch.setattr(
        "builtins.input", Mock(side_effect=lambda prompt: next(answers))
    )

    with patch("src.main.AIClient") as ai_client_class, patch(
        "src.scraping.wikipedia_client.requests.get", return_value=ARTICLE_RESPONSE
    ):
        ai_client_class.return_value.generate_text.side_effect = EnrichmentError(
            expected_message
        )
        main()

    output = capsys.readouterr().out
    assert "Árbol\n\nPrimer párrafo.\n" in output
    assert f"{expected_message}\n{ORIGINAL_KEPT_MESSAGE}\n" in output
    assert ENRICHED_HEADER not in output
    assert output.endswith("Programa finalizado.\n")