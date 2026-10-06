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


def test_extract_paragraphs_returns_first_five_article_paragraphs() -> None:
    html = """
    <html>
      <body>
        <nav><p>Navegación global</p></nav>
        <div id="mw-content-text">
          <div class="mw-parser-output">
            <table class="infobox">
              <tr><td><p>Texto de la infobox</p></td></tr>
            </table>
            <p>   </p>
            <p>Primer párrafo.</p>
            <div class="navbox"><p>Navegación interna</p></div>
            <p>Segundo párrafo.</p>
            <p>Tercer párrafo.</p>
            <p>Cuarto párrafo.</p>
            <p>Quinto párrafo.</p>
            <p>Sexto párrafo.</p>
          </div>
        </div>
        <footer><p>Pie de página</p></footer>
      </body>
    </html>
    """

    paragraphs = WikipediaParser().extract_paragraphs(html)

    assert paragraphs == [
        "Primer párrafo.",
        "Segundo párrafo.",
        "Tercer párrafo.",
        "Cuarto párrafo.",
        "Quinto párrafo.",
    ]


def test_extract_paragraphs_returns_all_when_fewer_than_five() -> None:
    html = """
    <div id="mw-content-text">
      <div class="mw-parser-output">
        <p>Primer párrafo disponible.</p>
        <p></p>
        <p>Segundo párrafo disponible.</p>
      </div>
    </div>
    """

    paragraphs = WikipediaParser().extract_paragraphs(html)

    assert paragraphs == [
        "Primer párrafo disponible.",
        "Segundo párrafo disponible.",
    ]
