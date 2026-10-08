import dataclasses

import pytest

from src.settings import load_settings


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


def test_load_settings_fails_when_timeout_is_not_a_number(monkeypatch):
    monkeypatch.setenv("WIKIPEDIA_TIMEOUT", "abc")

    with pytest.raises(ValueError):
        load_settings()