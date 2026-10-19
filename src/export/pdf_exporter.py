from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from src.export.exporter import Exporter


class PdfExporter(Exporter):
    def __init__(self) -> None:
        styles = getSampleStyleSheet()
        self._title_style = ParagraphStyle(
            "DocumentTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            spaceAfter=18,
        )
        self._body_style = ParagraphStyle(
            "DocumentBody",
            parent=styles["BodyText"],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
        )

    def export(self, title: str, content: str, destination: Path) -> None:
        story = [Paragraph(escape(title), self._title_style), Spacer(1, 0.3 * cm)]
        for paragraph in content.split("\n\n"):
            text = paragraph.strip()
            if text:
                story.append(
                    Paragraph(escape(text).replace("\n", "<br/>"), self._body_style)
                )

        document = SimpleDocTemplate(
            str(destination),
            pagesize=A4,
            title=title,
            leftMargin=2.5 * cm,
            rightMargin=2.5 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.5 * cm,
        )
        document.build(story)