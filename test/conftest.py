"""Mantiene las pruebas independientes del tiempo configurado en el .env local."""

import pytest


@pytest.fixture(autouse=True)
def default_wikipedia_timeout(monkeypatch):
    monkeypatch.setenv("WIKIPEDIA_TIMEOUT", "10")
