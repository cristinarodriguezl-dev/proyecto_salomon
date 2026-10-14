"""Exporta artículos traducidos a archivos TXT o PDF."""

import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)
from xml.sax.saxutils import escape


class Exporter:
    """Guarda artículos en formato TXT o PDF."""

    def export(
        self,
        title: str,
        content: str,
        file_format: str,
    ) -> Path:
        """Guarda el contenido y devuelve la ruta del archivo."""
        if not title.strip():
            raise ValueError("El título no puede estar vacío.")

        if not content.strip():
            raise ValueError("No hay contenido para guardar.")

        file_format = file_format.strip().lower()

        if file_format not in {"txt", "pdf"}:
            raise ValueError("El formato debe ser TXT o PDF.")

        safe_title = re.sub(
            r'[<>:"/\\|?*\x00-\x1f]',
            "_",
            title,
        ).strip(" .")

        if not safe_title:
            safe_title = "articulo"

        output_dir = Path("exports")
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / f"{safe_title}.{file_format}"

        if file_format == "txt":
            file_path.write_text(
                f"{title}\n\n{content}\n",
                encoding="utf-8",
            )
        else:
            self._export_pdf(file_path, title, content)

        return file_path

    def _export_pdf(
        self,
        file_path: Path,
        title: str,
        content: str,
    ) -> None:
        """Genera un PDF con título y párrafos."""
        document = SimpleDocTemplate(
            str(file_path),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        story = [
            Paragraph(escape(title), styles["Title"]),
            Spacer(1, 0.5 * cm),
        ]

        for paragraph in content.split("\n"):
            if paragraph.strip():
                story.append(
                    Paragraph(
                        escape(paragraph),
                        styles["BodyText"],
                    )
                )
                story.append(Spacer(1, 0.2 * cm))
            else:
                story.append(Spacer(1, 0.2 * cm))

        document.build(story)
