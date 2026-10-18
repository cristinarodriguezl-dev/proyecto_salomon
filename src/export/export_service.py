"""Connects the selected format and destination to an exporter."""

from collections.abc import Mapping

from src.exceptions import ExportError
from src.export.exporter import Exporter
from src.export.txt_exporter import TxtExporter
from src.ui.export_destination_prompt import ExportDestination


class ExportService:
    """Save selected article text through the matching format implementation."""

    def __init__(self, exporters: Mapping[str, Exporter] | None = None) -> None:
        self.exporters = dict(exporters) if exporters is not None else {"txt": TxtExporter()}

    def export(self, title: str, content: str, destination: ExportDestination) -> None:
        exporter = self.exporters.get(destination.file_format)
        if exporter is None:
            raise ExportError(f"La exportación a {destination.file_format.upper()} aún no está disponible.")

        try:
            exporter.export(title, content, destination.path)
        except OSError as error:
            raise ExportError(f"No se pudo guardar '{destination.path}': {error}") from error