"""Comprueba que la configuración llega a las peticiones reales del flujo."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.main import main
from src.settings import INVALID_TIMEOUT_MESSAGE


@pytest.fixture
def terminal_and_ai(monkeypatch):
    topic = Mock(return_value="Árbol")
    monkeypatch.setattr("src.main.request_topic", topic)
    monkeypatch.setattr("src.main.SummaryConfirmationPrompt.ask", lambda self: False)
    monkeypatch.setattr("src.main.TranslationLanguagePrompt.ask", lambda self: None)
    monkeypatch.setattr("src.main.ExportConfirmationPrompt.ask", lambda self: False)
    monkeypatch.setattr(
        "src.main.SearchContinuationPrompt.ask_search_again", lambda self: False
    )
    with patch("src.main.AIClient") as ai_client:
        ai_client.return_value.generate_text.return_value = "Texto enriquecido."
        yield topic, ai_client


def article_response() -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response.encoding = "utf-8"
    response._content = (
        '<h1 id="firstHeading">Árbol</h1>'
        '<div id="mw-content-text"><div class="mw-parser-output">'
        '<p>Primer párrafo.</p></div></div>'
    ).encode("utf-8")
    return response


@pytest.mark.parametrize(("configured", "expected"), [("5", 5), (None, 10)])
def test_main_passes_configured_or_default_timeout_to_http(
    configured, expected, monkeypatch, capsys, terminal_and_ai
):
    if configured is None:
        monkeypatch.delenv("WIKIPEDIA_TIMEOUT", raising=False)
    else:
        monkeypatch.setenv("WIKIPEDIA_TIMEOUT", configured)

    with patch(
        "src.scraping.wikipedia_client.requests.get", return_value=article_response()
    ) as get:
        main()

    get.assert_called_once()
    assert get.call_args.kwargs["timeout"] == expected
    assert "Primer párrafo." in capsys.readouterr().out


def test_main_uses_configured_timeout_when_reporting_failure_and_retrying(
    monkeypatch, capsys, terminal_and_ai
):
    monkeypatch.setenv("WIKIPEDIA_TIMEOUT", "5")
    topic, _ = terminal_and_ai
    with patch(
        "src.scraping.wikipedia_client.requests.get",
        side_effect=[requests.exceptions.Timeout("agotado"), article_response()],
    ) as get:
        main()

    assert get.call_count == topic.call_count == 2
    assert all(call.kwargs["timeout"] == 5 for call in get.call_args_list)
    output = capsys.readouterr().out
    assert "tiempo de espera de 5 segundos" in output
    assert "Primer párrafo." in output
    assert output.endswith("Programa finalizado.\n")


@pytest.mark.parametrize("timeout", ["abc", "0", "-1"])
def test_main_reports_invalid_configuration_before_starting_clients(
    timeout, monkeypatch, capsys, terminal_and_ai
):
    monkeypatch.setenv("WIKIPEDIA_TIMEOUT", timeout)
    topic, ai_client = terminal_and_ai
    with patch("src.scraping.wikipedia_client.requests.get") as get:
        main()

    assert capsys.readouterr().out == (
        f"Error de configuración: {INVALID_TIMEOUT_MESSAGE}\n"
    )
    topic.assert_not_called()
    ai_client.assert_not_called()
    get.assert_not_called()
