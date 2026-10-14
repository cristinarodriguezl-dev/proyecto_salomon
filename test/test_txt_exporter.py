"""Tests for the TXT exporter."""

from pathlib import Path

from src.export.exporter import Exporter
from src.export.txt_exporter import TxtExporter

TITLE = "Árbol"
CONTENT = "Primer párrafo.\n\nSegundo párrafo con ñ, ¿tildes? y «comillas»."


def test_txt_exporter_follows_the_common_contract() -> None:
    assert isinstance(TxtExporter(), Exporter)


def test_export_writes_the_title_as_a_heading_before_the_content(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "salida.txt"

    TxtExporter().export(TITLE, CONTENT, destination)

    assert destination.read_text(encoding="utf-8") == f"Árbol\n=====\n\n{CONTENT}\n"


def test_export_keeps_paragraph_separation_and_special_characters(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "salida.txt"

    TxtExporter().export(TITLE, CONTENT, destination)

    saved_text = destination.read_text(encoding="utf-8")
    assert CONTENT in saved_text
