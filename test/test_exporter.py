"""Pruebas del contrato común de exportación."""

from pathlib import Path

import pytest

from src.export.exporter import Exporter


class RecordingExporter(Exporter):
    """Exportador falso que registra lo que recibe."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Path]] = []

    def export(self, title: str, content: str, destination: Path) -> None:
        self.calls.append((title, content, destination))


class FakeTxtExporter(RecordingExporter):
    """Representa una salida TXT."""


class FakePdfExporter(RecordingExporter):
    """Representa una salida PDF."""


class IncompleteExporter(Exporter):
    """Subclase que no implementa export."""


def save_document(exporter: Exporter) -> None:
    """Simula al servicio principal: solo conoce el contrato, no el formato."""
    exporter.export("Árbol", "Contenido.", Path("salida"))


def test_exporter_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        Exporter()


def test_exporter_subclass_without_export_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        IncompleteExporter()


@pytest.mark.parametrize("exporter_class", [FakeTxtExporter, FakePdfExporter])
def test_any_format_is_requested_through_the_same_contract(exporter_class) -> None:
    exporter = exporter_class()

    save_document(exporter)

    assert exporter.calls == [("Árbol", "Contenido.", Path("salida"))]