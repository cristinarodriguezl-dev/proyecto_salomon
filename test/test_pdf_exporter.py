from pathlib import Path

from src.export.exporter import Exporter
from src.export.pdf_exporter import PdfExporter

TITLE = "Árbol"
CONTENT = "Primer párrafo.\n\nSegundo párrafo con ñ, ¿tildes? y «comillas» & <etiquetas>."


def test_pdf_exporter_follows_the_common_contract() -> None:
    assert isinstance(PdfExporter(), Exporter)


def test_export_creates_a_valid_pdf_file(tmp_path: Path) -> None:
    destination = tmp_path / "salida.pdf"

    PdfExporter().export(TITLE, CONTENT, destination)

    assert destination.exists()
    assert destination.read_bytes().startswith(b"%PDF")


def test_export_accepts_special_characters_and_markup_symbols(tmp_path: Path) -> None:
    destination = tmp_path / "salida.pdf"

    PdfExporter().export(TITLE, CONTENT, destination)

    assert destination.stat().st_size > 0


def test_export_handles_long_content_over_several_pages(tmp_path: Path) -> None:
    destination = tmp_path / "largo.pdf"
    long_content = "\n\n".join(f"Párrafo número {i}. " * 40 for i in range(60))

    PdfExporter().export(TITLE, long_content, destination)

    assert destination.read_bytes().count(b"/Type /Page\n") > 1