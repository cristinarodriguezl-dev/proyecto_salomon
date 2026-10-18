"""Tests for the messages TranslationService raises when MyMemory cannot be used."""

from unittest.mock import patch

import pytest
import requests

from src.exceptions import TranslationError
from src.translation.translation_service import (
    CONNECTION_ERROR_MESSAGE,
    SERVICE_ERROR_MESSAGE,
    TranslationService,
)

LONG_ERROR_TEXT = "HTTPSConnectionPool(host='api.mymemory.translated.net'): q=Hola"


@pytest.mark.parametrize(
    ("network_error", "expected_message"),
    [
        (requests.exceptions.ConnectionError(LONG_ERROR_TEXT), CONNECTION_ERROR_MESSAGE),
        (requests.exceptions.Timeout("timed out"), CONNECTION_ERROR_MESSAGE),
        (requests.exceptions.HTTPError("503 Server Error"), SERVICE_ERROR_MESSAGE),
    ],
    ids=["connection_error", "timeout", "http_error"],
)
def test_translate_explains_each_kind_of_failure(
    network_error, expected_message
) -> None:
    with patch("src.translation.translation_service.requests.get") as get:
        get.side_effect = network_error

        with pytest.raises(TranslationError) as raised:
            TranslationService().translate("Hola", target_language="en")

    assert str(raised.value) == expected_message


def test_translate_does_not_show_the_technical_error_to_the_user() -> None:
    with patch("src.translation.translation_service.requests.get") as get:
        get.side_effect = requests.exceptions.ConnectionError(LONG_ERROR_TEXT)

        with pytest.raises(TranslationError) as raised:
            TranslationService().translate("Hola", target_language="en")

    assert "HTTPSConnectionPool" not in str(raised.value)
    assert "Hola" not in str(raised.value)


def test_unsupported_language_is_not_reported_as_a_translation_failure() -> None:
    with patch("src.translation.translation_service.requests.get") as get:
        with pytest.raises(ValueError, match="Idioma no admitido") as raised:
            TranslationService().translate("Hola", target_language="klingon")

    assert not isinstance(raised.value, TranslationError)
    get.assert_not_called()