"""Pruebas de integración del flujo de búsqueda y enriquecimiento en la terminal."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.main import main
from src.scraping.wikipedia_client import USER_AGENT, WIKIPEDIA_SEARCH_URL
from src.ui.article_display import ENRICHED_HEADER

ENRICHED_TEXT = "Texto enriquecido por IA."


def make_response(html: str, status_code: int = 200) -> requests.Response:
    """Crea una respuesta HTTP local para probar sin red."""
    response = requests.Response()
    response.status_code = status_code
    response.url = WIKIPEDIA_SEARCH_URL
    response._content = html.encode("utf-8")
    return response


SUCCESS_RESPONSE = make_response(
    """
    <h1 id="firstHeading">Árbol</h1>
    <div id="mw-content-text"><div class="mw-parser-output">
      <p>Primer párrafo.</p>
      <p>Segundo párrafo.</p>
    </div></div>
    """
)

ARTICLE_OUTPUT = (
    "Árbol\n=====\n\nPrimer párrafo.\n\nSegundo párrafo.\n"
    f"{ENRICHED_HEADER}\n\n{ENRICHED_TEXT}\n"
)
CONTINUATION_MENU_OUTPUT = (
    "\n¿Qué quieres hacer ahora?\n1. Buscar otro tema\n2. Salir\n"
)
EXIT_OUTPUT = "Programa finalizado.\n"

NO_ARTICLE_RESPONSE = make_response(
    """
    <h1 id="firstHeading">Resultados de búsqueda</h1>
    <div id="mw-content-text"><div class="mw-parser-output"></div></div>
    """
)

NO_TITLE_RESPONSE = make_response(
    """
    <html>
      <head><title>Wikipedia</title></head>
      <body><div id="mw-content-text"></div></body>
    </html>
    """
)

AMBIGUOUS_RESPONSE = make_response(
    """
    <h1 id="firstHeading">Mercurio</h1>
    <div id="mw-content-text"><div class="mw-parser-output">
      <p>Mercurio puede referirse a distintos temas.</p>
    </div></div>
    <div id="catlinks">
      <a href="/wiki/Categoría:Wikipedia:Desambiguación">
        Wikipedia:Desambiguación
      </a>
    </div>
    """
)


@pytest.fixture
def fake_ai_client():
    """Sustituye el cliente de Gemini por uno falso para no llamar a la API."""
    with patch("src.main.AIClient") as ai_client_class, patch(
        "src.main.TranslationLanguagePrompt"
    ) as language_prompt_class:
        ai_client_class.return_value.generate_text.return_value = ENRICHED_TEXT
        language_prompt_class.return_value.ask.return_value = None
        yield ai_client_class.return_value


def test_main_searches_and_displays_the_original_and_enriched_article(
        monkeypatch, capsys, fake_ai_client
) -> None:
    answers = iter(["  Árbol  ", "n", "2"])
    fake_input = Mock(side_effect=lambda prompt: next(answers))
    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setenv("WIKIPEDIA_TIMEOUT", "10")

    with patch(
            "src.scraping.wikipedia_client.requests.get",
            return_value=SUCCESS_RESPONSE,
    ) as get:
        main()

    get.assert_called_once_with(
        WIKIPEDIA_SEARCH_URL,
        params={"search": "Árbol"},
        headers={"User-Agent": USER_AGENT},
        timeout=10.0,
    )
    assert fake_input.call_count == 3
    fake_ai_client.generate_text.assert_called_once()
    assert capsys.readouterr().out == (
            ARTICLE_OUTPUT + CONTINUATION_MENU_OUTPUT + EXIT_OUTPUT
    )


@pytest.mark.parametrize(
    ("first_attempt", "expected_error"),
    [
        (
                requests.exceptions.ConnectionError("Conexión rechazada"),
                "No se pudo conectar con Wikipedia: Conexión rechazada",
        ),
        (
                make_response("Error de servidor", status_code=503),
                "Wikipedia respondió con un error HTTP (código 503).",
        ),
    ],
    ids=["connection-error", "http-error"],
)
def test_main_reports_wikipedia_error_and_allows_another_search(
        first_attempt, expected_error: str, monkeypatch, capsys, fake_ai_client
) -> None:
    answers = iter(["Árbol", "Música", "n", "2"])
    fake_input = Mock(side_effect=lambda prompt: next(answers))
    monkeypatch.setattr("builtins.input", fake_input)

    with patch(
            "src.scraping.wikipedia_client.requests.get",
            side_effect=[first_attempt, SUCCESS_RESPONSE],
    ) as get:
        main()

    assert get.call_count == 2
    assert fake_input.call_count == 4
    fake_ai_client.generate_text.assert_called_once()
    assert capsys.readouterr().out == (
            f"{expected_error}\n"
            + ARTICLE_OUTPUT
            + CONTINUATION_MENU_OUTPUT
            + EXIT_OUTPUT
    )


def test_main_allows_another_search_and_then_exits(
        monkeypatch, capsys, fake_ai_client
) -> None:
    answers = iter(["Árbol", "n", "1", "Música", "n", "2"])
    fake_input = Mock(side_effect=lambda prompt: next(answers))
    monkeypatch.setattr("builtins.input", fake_input)

    with patch(
            "src.scraping.wikipedia_client.requests.get",
            side_effect=[SUCCESS_RESPONSE, SUCCESS_RESPONSE],
    ) as get:
        main()

    assert get.call_count == 2
    assert fake_input.call_count == 6
    assert fake_ai_client.generate_text.call_count == 2
    assert capsys.readouterr().out == (
            ARTICLE_OUTPUT
            + CONTINUATION_MENU_OUTPUT
            + ARTICLE_OUTPUT
            + CONTINUATION_MENU_OUTPUT
            + EXIT_OUTPUT
    )


def test_main_reports_missing_or_ambiguous_article_and_allows_another_search(
    monkeypatch, capsys, fake_ai_client
) -> None:
    answers = iter(
        ["tema inexistente", "tema sin contenido", "Mercurio", "Árbol", "n", "2"]
    )
    fake_input = Mock(side_effect=lambda prompt: next(answers))
    monkeypatch.setattr("builtins.input", fake_input)

    with patch(
        "src.scraping.wikipedia_client.requests.get",
        side_effect=[
            NO_TITLE_RESPONSE,
            NO_ARTICLE_RESPONSE,
            AMBIGUOUS_RESPONSE,
            SUCCESS_RESPONSE,
        ],
    ) as get:
        main()

    assert get.call_count == 4
    assert fake_input.call_count == 6
    fake_ai_client.generate_text.assert_called_once()
    assert capsys.readouterr().out == (
        'No se encontró un artículo válido para "tema inexistente". Prueba otra búsqueda.\n'
        'No se encontró un artículo válido para "tema sin contenido". Prueba otra búsqueda.\n'
        'El tema "Mercurio" es ambiguo. Prueba con un nombre más específico '
        'o añade una palabra que indique a qué te refieres.\n'
        + ARTICLE_OUTPUT
        + CONTINUATION_MENU_OUTPUT
        + EXIT_OUTPUT
    )


def test_main_exports_selected_enriched_text_and_can_search_again(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    answers = iter(["Árbol", "s", "2", "txt", "articulo", "1", "Música", "n", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    with patch(
        "src.scraping.wikipedia_client.requests.get",
        side_effect=[SUCCESS_RESPONSE, SUCCESS_RESPONSE],
    ) as get:
        main()

    assert get.call_count == 2
    assert (tmp_path / "articulo.txt").read_text(encoding="utf-8") == (
        "Árbol\n=====\n\nTexto enriquecido por IA.\n"
    )
    assert "Archivo guardado: articulo.txt" in capsys.readouterr().out


def test_main_reports_unavailable_pdf_and_still_exits(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    answers = iter(["Árbol", "s", "1", "pdf", "articulo", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    with patch(
        "src.scraping.wikipedia_client.requests.get", return_value=SUCCESS_RESPONSE
    ):
        main()

    assert not (tmp_path / "articulo.pdf").exists()
    output = capsys.readouterr().out
    assert "La exportación a PDF aún no está disponible." in output
    assert output.endswith(EXIT_OUTPUT)


def test_main_replaces_an_existing_document_when_overwrite_is_confirmed(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / "articulo.txt"
    existing.write_text("Versión anterior", encoding="utf-8")
    answers = iter(["Árbol", "s", "1", "txt", "articulo", "s", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    with patch(
        "src.scraping.wikipedia_client.requests.get", return_value=SUCCESS_RESPONSE
    ):
        main()

    saved = existing.read_text(encoding="utf-8")
    assert "Versión anterior" not in saved
    assert saved.startswith("Árbol\n=====")
    output = capsys.readouterr().out
    assert "Archivo guardado: articulo.txt" in output
    assert output.endswith(EXIT_OUTPUT)


def test_main_keeps_an_existing_document_when_overwrite_is_rejected(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / "articulo.txt"
    existing.write_text("Versión anterior", encoding="utf-8")
    answers = iter(["Árbol", "s", "1", "txt", "articulo", "n", "otro", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    with patch(
        "src.scraping.wikipedia_client.requests.get", return_value=SUCCESS_RESPONSE
    ):
        main()

    assert existing.read_text(encoding="utf-8") == "Versión anterior"
    assert (tmp_path / "otro.txt").exists()
    output = capsys.readouterr().out
    assert "Archivo guardado: otro.txt" in output
    assert output.endswith(EXIT_OUTPUT)


def test_main_allows_another_search_after_an_export_error(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    answers = iter(["Árbol", "s", "1", "txt", "articulo", "1", "Música", "n", "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    with patch(
        "src.scraping.wikipedia_client.requests.get",
        side_effect=[SUCCESS_RESPONSE, SUCCESS_RESPONSE],
    ) as get, patch(
        "src.export.txt_exporter.TxtExporter.export",
        side_effect=PermissionError("sin permiso"),
    ):
        main()

    assert get.call_count == 2
    assert not (tmp_path / "articulo.txt").exists()
    output = capsys.readouterr().out
    assert "No se pudo guardar 'articulo.txt': sin permiso" in output
    assert output.endswith(EXIT_OUTPUT)