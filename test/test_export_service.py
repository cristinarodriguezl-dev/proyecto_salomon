"""Check that export choices reach the appropriate exporter."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from pypdf import PdfReader

from src.exceptions import ExportError
from src.export.export_service import ExportService
from src.export.exporter import Exporter
from src.export.txt_exporter import TxtExporter
from src.ui.export_destination_prompt import ExportDestination


def test_default_service_exports_pdf_with_title_and_selected_content(
    tmp_path: Path,
) -> None:
    destination = ExportDestination("pdf", tmp_path / "articulo.pdf")

    ExportService().export("Árbol", "Contenido elegido para PDF.", destination)

    assert destination.path.read_bytes().startswith(b"%PDF")
    reader = PdfReader(destination.path)
    assert len(reader.pages) == 1
    pdf_text = reader.pages[0].extract_text()
    assert "Árbol" in pdf_text
    assert "Contenido elegido para PDF." in pdf_text


def test_service_dispatches_pdf_to_a_registered_exporter(tmp_path: Path) -> None:
    pdf_exporter = Mock(spec=Exporter)
    service = ExportService({"pdf": pdf_exporter})
    destination = ExportDestination("pdf", tmp_path / "articulo.pdf")

    service.export("Árbol", "Contenido elegido", destination)

    pdf_exporter.export.assert_called_once_with(
        "Árbol", "Contenido elegido", destination.path
    )


def test_service_reports_write_errors_as_export_errors(tmp_path: Path) -> None:
    txt_exporter = Mock(spec=Exporter)
    txt_exporter.export.side_effect = PermissionError("sin permiso")
    service = ExportService({"txt": txt_exporter})
    destination = ExportDestination("txt", tmp_path / "articulo.txt")

    with pytest.raises(ExportError, match="No se pudo guardar.*sin permiso"):
        service.export("Árbol", "Contenido", destination)


def test_service_replaces_an_existing_file_with_the_new_content(
    tmp_path: Path,
) -> None:
    destination = ExportDestination("txt", tmp_path / "articulo.txt")
    destination.path.write_text("Versión anterior", encoding="utf-8")
    service = ExportService({"txt": TxtExporter()})

    service.export("Árbol", "Contenido nuevo", destination)

    saved = destination.path.read_text(encoding="utf-8")
    assert "Versión anterior" not in saved
    assert "Contenido nuevo" in saved


def test_injected_exporters_do_not_fall_back_to_the_default_pdf_exporter(
    tmp_path: Path,
) -> None:
    txt_exporter = Mock(spec=Exporter)
    service = ExportService({"txt": txt_exporter})
    destination = ExportDestination("pdf", tmp_path / "articulo.pdf")

    with pytest.raises(ExportError, match="PDF aún no está disponible"):
        service.export("Árbol", "Contenido", destination)

    txt_exporter.export.assert_not_called()
    assert not destination.path.exists()


def test_an_explicit_empty_exporter_map_disables_default_formats(
    tmp_path: Path,
) -> None:
    destination = ExportDestination("txt", tmp_path / "articulo.txt")

    with pytest.raises(ExportError, match="TXT aún no está disponible"):
        ExportService({}).export("Árbol", "Contenido", destination)

    assert not destination.path.exists()
