"""Pruebas unitarias del servicio MyMemory sin llamadas de red."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.exceptions import TranslationError
from src.translation.translation_service import TranslationService


def make_response(translation: str = "Hello", status: int = 200) -> Mock:
    response = Mock()
    response.json.return_value = {
        "responseStatus": status,
        "responseDetails": "Unsupported language pair" if status != 200 else "OK",
        "responseData": {"translatedText": translation},
    }
    return response


def test_get_supported_languages_returns_a_copy_of_available_options() -> None:
    service = TranslationService()

    languages = service.get_supported_languages()

    assert languages["en"] == "Inglés"
    assert languages["es"] == "Español"
    languages.clear()
    assert "en" in service.get_supported_languages()


@patch("src.translation.translation_service.requests.get")
def test_translate_sends_valid_pair_and_returns_translation(get) -> None:
    get.return_value = make_response("Hello")

    result = TranslationService().translate("Hola", target_language="en")

    assert result == "Hello"
    get.assert_called_once_with(
        TranslationService.API_URL,
        params={"q": "Hola", "langpair": "es|en"},
        timeout=20,
    )


@patch("src.translation.translation_service.requests.get")
def test_translate_accepts_a_supported_language_name(get) -> None:
    get.return_value = make_response("Bonjour")

    result = TranslationService().translate("Hola", target_language="Francés")

    assert result == "Bonjour"
    assert get.call_args.kwargs["params"]["langpair"] == "es|fr"


@patch("src.translation.translation_service.requests.get")
def test_translate_rejects_a_language_not_in_the_supported_list(get) -> None:
    with pytest.raises(ValueError, match="Idioma no admitido"):
        TranslationService().translate("Hola", target_language="xx")

    get.assert_not_called()


@patch("src.translation.translation_service.requests.get")
def test_translate_wraps_connection_failure_as_translation_error(get) -> None:
    get.side_effect = requests.exceptions.Timeout("timed out")

    with pytest.raises(TranslationError, match="MyMemory"):
        TranslationService().translate("Hola", target_language="en")


@patch("src.translation.translation_service.requests.get")
def test_translate_wraps_http_failure_as_translation_error(get) -> None:
    response = make_response()
    response.raise_for_status.side_effect = requests.exceptions.HTTPError("503")
    get.return_value = response

    with pytest.raises(TranslationError, match="MyMemory"):
        TranslationService().translate("Hola", target_language="en")


@patch("src.translation.translation_service.requests.get")
def test_translate_reports_provider_failure(get) -> None:
    get.return_value = make_response(status=429)

    with pytest.raises(TranslationError, match="Unsupported language pair"):
        TranslationService().translate("Hola", target_language="en")


@patch("src.translation.translation_service.requests.get")
def test_translate_reports_missing_translation(get) -> None:
    get.return_value = make_response(translation="")

    with pytest.raises(TranslationError, match="no ha devuelto"):
        TranslationService().translate("Hola", target_language="en")


@patch("src.translation.translation_service.time.sleep")
@patch("src.translation.translation_service.requests.get")
def test_translate_splits_long_text_without_exceeding_request_limit(
    get, _sleep
) -> None:
    get.side_effect = [make_response("First"), make_response("second")]
    content = "palabra " * 100

    result = TranslationService().translate(content, target_language="en")

    assert result == "First second"
    assert get.call_count == 2
    assert all(
        len(request.kwargs["params"]["q"]) <= TranslationService.MAX_CHUNK_SIZE
        for request in get.call_args_list
    )


@patch("src.translation.translation_service.requests.get")
def test_translate_rejects_a_single_word_over_the_request_limit(get) -> None:
    content = "x" * (TranslationService.MAX_CHUNK_SIZE + 1)

    with pytest.raises(ValueError, match="supera el límite"):
        TranslationService().translate(content, target_language="en")

    get.assert_not_called()
