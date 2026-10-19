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


def test_service_creates_the_missing_export_directory(tmp_path: Path) -> None:
    destination = ExportDestination("txt", tmp_path / "exports" / "articulo.txt")
    service = ExportService({"txt": TxtExporter()})

    service.export("Árbol", "Contenido", destination)

    assert destination.path.exists()


def test_service_reports_a_directory_that_cannot_be_created_as_export_error(
    tmp_path: Path,
) -> None:
    (tmp_path / "exports").write_text("no es una carpeta", encoding="utf-8")
    destination = ExportDestination("txt", tmp_path / "exports" / "articulo.txt")
    service = ExportService({"txt": TxtExporter()})

    with pytest.raises(ExportError, match="No se pudo guardar"):
        service.export("Árbol", "Contenido", destination)


def test_service_reports_a_directory_without_permission_as_export_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "mkdir", Mock(side_effect=PermissionError("sin permiso")))
    destination = ExportDestination("txt", tmp_path / "exports" / "articulo.txt")
    service = ExportService({"txt": TxtExporter()})

    with pytest.raises(ExportError, match="No se pudo guardar.*sin permiso"):
        service.export("Árbol", "Contenido", destination)