"""Pruebas de errores HTTP del cliente sin acceder a Wikipedia."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.scraping.wikipedia_client import WikipediaClient


def test_fetch_reports_connection_error() -> None:
    request_error = requests.exceptions.ConnectionError("Conexión rechazada")

    with patch(
        "src.scraping.wikipedia_client.requests.get", side_effect=request_error
    ) as get:
        with pytest.raises(
            requests.exceptions.ConnectionError,
            match="No se pudo conectar con Wikipedia",
        ) as error:
            WikipediaClient().fetch("Árbol")

    assert str(error.value) == (
        "No se pudo conectar con Wikipedia: Conexión rechazada"
    )
    assert error.value.__cause__ is request_error
    get.assert_called_once()


def test_fetch_reports_http_status_error() -> None:
    response = Mock(spec=requests.Response)
    response.status_code = 503
    request_error = requests.exceptions.HTTPError("503 Server Error", response=response)
    response.raise_for_status.side_effect = request_error

    with patch(
        "src.scraping.wikipedia_client.requests.get", return_value=response
    ) as get:
        with pytest.raises(
            requests.exceptions.HTTPError,
            match=r"error HTTP \(código 503\)",
        ) as error:
            WikipediaClient().fetch("Árbol")

    assert str(error.value) == (
        "Wikipedia respondió con un error HTTP (código 503)."
    )
    assert error.value.response is response
    assert error.value.__cause__ is request_error
    response.raise_for_status.assert_called_once_with()
    get.assert_called_once()
