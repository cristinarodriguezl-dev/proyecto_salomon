"""Check that export choices reach the appropriate exporter."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.exceptions import ExportError
from src.export.export_service import ExportService
from src.export.exporter import Exporter
from src.ui.export_destination_prompt import ExportDestination


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
