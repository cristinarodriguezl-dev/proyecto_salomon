"""Pruebas de integración del flujo de búsqueda y enriquecimiento en la terminal."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.main import main
from src.scraping.wikipedia_client import USER_AGENT, WIKIPEDIA_SEARCH_URL
from src.ui.article_display import ENRICHED_HEADER

ENRICHED_TEXT = "Texto enriquecido por IA."


def make_response(html: str, status_code: int = 200) -> requests.Response:
    """Crea una respuesta HTTP local para probar sin red."""
    response = requests.Response()
    response.status_code = status_code
    response.url = WIKIPEDIA_SEARCH_URL
    response._content = html.encode("utf-8")
    return response


SUCCESS_RESPONSE = make_response(
    """
    <h1 id="firstHeading">Árbol</h1>
    <div id="mw-content-text"><div class="mw-parser-output">
      <p>Primer párrafo.</p>
      <p>Segundo párrafo.</p>
    </div></div>
    """
)

EXPECTED_ARTICLE_OUTPUT = (
    "Árbol\n\nPrimer párrafo.\n\nSegundo párrafo.\n"
    f"{ENRICHED_HEADER}\n\n{ENRICHED_TEXT}\n"
)


@pytest.fixture(autouse=True)
def fake_ai_client():
    """Sustituye el cliente de Gemini por uno falso para no llamar a la API."""
    with patch("src.main.AIClient") as ai_client_class:
        ai_client_class.return_value.generate_text.return_value = ENRICHED_TEXT
        yield ai_client_class.return_value


def test_main_searches_and_displays_the_original_and_enriched_article(
    monkeypatch, capsys, fake_ai_client
) -> None:
    fake_input = Mock(return_value="  Árbol  ")
    monkeypatch.setattr("builtins.input", fake_input)

    with patch(
        "src.scraping.wikipedia_client.requests.get",
        return_value=SUCCESS_RESPONSE,
    ) as get:
        main()

    get.assert_called_once_with(
        WIKIPEDIA_SEARCH_URL,
        params={"search": "Árbol"},
        headers={"User-Agent": USER_AGENT},
        timeout=10.0,
    )
    fake_input.assert_called_once()
    fake_ai_client.generate_text.assert_called_once()
    assert capsys.readouterr().out == EXPECTED_ARTICLE_OUTPUT


@pytest.mark.parametrize(
    ("first_attempt", "expected_error"),
    [
        (
            requests.exceptions.ConnectionError("Conexión rechazada"),
            "No se pudo conectar con Wikipedia: Conexión rechazada",
        ),
        (
            make_response("Error de servidor", status_code=503),
            "Wikipedia respondió con un error HTTP (código 503).",
        ),
    ],
    ids=["connection-error", "http-error"],
)
def test_main_reports_wikipedia_error_and_allows_another_search(
    first_attempt, expected_error: str, monkeypatch, capsys, fake_ai_client
) -> None:
    answers = iter(["Árbol", "Música"])
    fake_input = Mock(side_effect=lambda prompt: next(answers))
    monkeypatch.setattr("builtins.input", fake_input)

    with patch(
        "src.scraping.wikipedia_client.requests.get",
        side_effect=[first_attempt, SUCCESS_RESPONSE],
    ) as get:
        main()

    assert get.call_count == 2
    assert fake_input.call_count == 2
    fake_ai_client.generate_text.assert_called_once()
    assert capsys.readouterr().out == f"{expected_error}\n{EXPECTED_ARTICLE_OUTPUT}"
