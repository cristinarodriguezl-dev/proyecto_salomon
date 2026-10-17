"""Saves a document in a plain text (TXT) file."""

from pathlib import Path

from src.export.exporter import Exporter


class TxtExporter(Exporter):
    """Writes the title as a heading followed by the content in a UTF-8 file."""

    def export(self, title: str, content: str, destination: Path) -> None:
        """Save the title, a blank line and the content in the destination file."""
        heading = f"{title}\n{'=' * len(title)}"
        destination.write_text(f"{heading}\n\n{content}\n", encoding="utf-8")