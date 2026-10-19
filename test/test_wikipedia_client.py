"""Pruebas de la consulta HTTP a Wikipedia sin acceso a la red."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.scraping.wikipedia_client import (
    USER_AGENT,
    WIKIPEDIA_SEARCH_URL,
    WikipediaClient,
)


def test_fetch_returns_valid_response() -> None:
    response = Mock(spec=requests.Response)

    with patch("src.scraping.wikipedia_client.requests.get", return_value=response) as get:
        result = WikipediaClient().fetch("Árbol")

    assert result is response
    get.assert_called_once_with(
        WIKIPEDIA_SEARCH_URL,
        params={"search": "Árbol"},
        headers={"User-Agent": USER_AGENT},
        timeout=10.0,
    )


def test_fetch_reports_timeout() -> None:
    request_timeout = requests.exceptions.Timeout("Sin respuesta")

    with patch(
        "src.scraping.wikipedia_client.requests.get", side_effect=request_timeout
    ) as get:
        with pytest.raises(TimeoutError, match="0.5 segundos") as error:
            WikipediaClient(timeout_seconds=0.5).fetch("Árbol")

    assert error.value.__cause__ is request_timeout
    get.assert_called_once_with(
        WIKIPEDIA_SEARCH_URL,
        params={"search": "Árbol"},
        headers={"User-Agent": USER_AGENT},
        timeout=0.5,
    )
