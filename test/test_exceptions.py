import pytest

from src.exceptions import (
    ContentEnricherError,
    EnrichmentError,
    ExportError,
    SearchError,
    TranslationError,
)

SPECIFIC_ERRORS = [SearchError, EnrichmentError, TranslationError, ExportError]


@pytest.mark.parametrize("error_class", SPECIFIC_ERRORS)
def test_specific_errors_can_be_caught_as_project_errors(error_class):
    with pytest.raises(ContentEnricherError):
        raise error_class("something failed")


@pytest.mark.parametrize("error_class", SPECIFIC_ERRORS)
def test_specific_errors_keep_their_message(error_class):
    error = error_class("something failed")

    assert str(error) == "something failed"


def test_each_error_is_different_from_the_others():
    with pytest.raises(SearchError):
        try:
            raise SearchError("Wikipedia is unavailable")
        except EnrichmentError:
            pytest.fail("A SearchError must not be caught as EnrichmentError")