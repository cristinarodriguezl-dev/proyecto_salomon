"""Pruebas del procesamiento de HTML de Wikipedia."""

import pytest

from src.scraping.wikipedia_parser import WikipediaParser


def test_extract_title_returns_article_heading() -> None:
    html = """
    <html>
      <head><title>Árbol - Wikipedia, la enciclopedia libre</title></head>
      <body>
        <header><h1>Wikipedia</h1></header>
        <h2>Contenido</h2>
        <h1 id="firstHeading"><span>Árbol</span></h1>
      </body>
    </html>
    """

    title = WikipediaParser().extract_title(html)

    assert title == "Árbol"
    assert "Wikipedia" not in title


def test_extract_title_reports_missing_article_heading() -> None:
    html = """
    <html>
      <head><title>Wikipedia, la enciclopedia libre</title></head>
      <body><h1>Otro encabezado</h1></body>
    </html>
    """

    with pytest.raises(ValueError, match="No se encontró un título válido"):
        WikipediaParser().extract_title(html)
