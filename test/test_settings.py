import dataclasses

import pytest

from src.settings import INVALID_TIMEOUT_MESSAGE, load_settings


def test_load_settings_reads_values_from_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("WIKIPEDIA_TIMEOUT", "5")

    settings = load_settings()

    assert settings.gemini_api_key == "test-key"

    assert settings.wikipedia_timeout == 5


def test_load_settings_uses_defaults_when_variables_are_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("WIKIPEDIA_TIMEOUT", raising=False)

    settings = load_settings()

    assert settings.gemini_api_key == ""
    assert settings.wikipedia_timeout == 10


def test_settings_cannot_be_modified_after_creation(monkeypatch):
    monkeypatch.setenv("WIKIPEDIA_TIMEOUT", "5")
    settings = load_settings()

    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.wikipedia_timeout = 20


@pytest.mark.parametrize("timeout", ["abc", "", "1.5", "0", "00", "-1"])
def test_load_settings_rejects_invalid_timeout(monkeypatch, timeout):
    monkeypatch.setenv("WIKIPEDIA_TIMEOUT", timeout)

    with pytest.raises(ValueError, match=INVALID_TIMEOUT_MESSAGE):
        load_settings()
