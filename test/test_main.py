"""Pruebas de integración del flujo de búsqueda y enriquecimiento en la terminal."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
import questionary
import requests
from pypdf import PdfReader

from src.main import main
from src.scraping.wikipedia_client import USER_AGENT, WIKIPEDIA_SEARCH_URL
from src.ui.article_display import ENRICHED_HEADER
from src.ui.export_destination_prompt import EXPORT_DIRECTORY

ENRICHED_TEXT = "Texto enriquecido por IA."


def install_questionary(monkeypatch, answers):
    """Sustituye las preguntas de questionary por respuestas fijas."""
    pending = iter(answers)
    prompts = SimpleNamespace(messages=[], choices=[])

    def question(message, *args, **kwargs):
        prompts.messages.append(message)
        prompts.choices.append(kwargs.get("choices"))
        return SimpleNamespace(unsafe_ask=lambda: next(pending))

    for name in ("text", "select", "confirm"):
        monkeypatch.setattr(questionary, name, question)

    return prompts



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
    "Árbol\n\nPrimer párrafo.\n\nSegundo párrafo.\n"
    f"{ENRICHED_HEADER}\n\n{ENRICHED_TEXT}\n"
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
    ) as language_prompt_class, patch(
        "src.main.SummaryConfirmationPrompt"
    ) as summary_prompt_class:
        ai_client_class.return_value.generate_text.return_value = ENRICHED_TEXT
        language_prompt_class.return_value.ask.return_value = None
        summary_prompt_class.return_value.ask.return_value = False
        yield ai_client_class.return_value


def test_main_searches_and_displays_the_original_and_enriched_article(
        monkeypatch, capsys, fake_ai_client
) -> None:
    answers = ["  Árbol  ", "No", "Salir"]
    prompts = install_questionary(monkeypatch, answers)
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
    assert len(prompts.messages) == 3
    fake_ai_client.generate_text.assert_called_once()
    assert capsys.readouterr().out == (ARTICLE_OUTPUT + EXIT_OUTPUT)


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
    answers = ["Árbol", "Música", "No", "Salir"]
    prompts = install_questionary(monkeypatch, answers)

    with patch(
            "src.scraping.wikipedia_client.requests.get",
            side_effect=[first_attempt, SUCCESS_RESPONSE],
    ) as get:
        main()

    assert get.call_count == 2
    assert len(prompts.messages) == 4
    fake_ai_client.generate_text.assert_called_once()
    assert capsys.readouterr().out == (
            f"{expected_error}\n" + ARTICLE_OUTPUT + EXIT_OUTPUT
    )


def test_main_allows_another_search_and_then_exits(
        monkeypatch, capsys, fake_ai_client
) -> None:
    answers = ["Árbol", "No", "Buscar otro tema", "Música", "No", "Salir"]
    prompts = install_questionary(monkeypatch, answers)

    with patch(
            "src.scraping.wikipedia_client.requests.get",
            side_effect=[SUCCESS_RESPONSE, SUCCESS_RESPONSE],
    ) as get:
        main()

    assert get.call_count == 2
    assert len(prompts.messages) == 6
    assert fake_ai_client.generate_text.call_count == 2
    assert capsys.readouterr().out == (
            ARTICLE_OUTPUT
            + ARTICLE_OUTPUT
            + EXIT_OUTPUT
    )


def test_main_reports_missing_or_ambiguous_article_and_allows_another_search(
    monkeypatch, capsys, fake_ai_client
) -> None:
    answers = [
        "tema inexistente",
        "tema sin contenido",
        "Mercurio",
        "Árbol",
        "No",
        "Salir",
    ]
    prompts = install_questionary(monkeypatch, answers)

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
    assert len(prompts.messages) == 6
    fake_ai_client.generate_text.assert_called_once()
    assert capsys.readouterr().out == (
        'No se encontró un artículo válido para "tema inexistente". Prueba otra búsqueda.\n'
        'No se encontró un artículo válido para "tema sin contenido". Prueba otra búsqueda.\n'
        'El tema "Mercurio" es ambiguo. Prueba con un nombre más específico '
        'o añade una palabra que indique a qué te refieres.\n'
        + ARTICLE_OUTPUT
        + EXIT_OUTPUT
    )


def test_main_exports_selected_enriched_text_and_can_search_again(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    answers = [
        "Árbol", "Sí", "Enriquecida", "TXT", "articulo",
        "Buscar otro tema", "Música", "No", "Salir",
    ]
    install_questionary(monkeypatch, answers)

    with patch(
            "src.scraping.wikipedia_client.requests.get",
            side_effect=[SUCCESS_RESPONSE, SUCCESS_RESPONSE],
    ) as get:
        main()

    assert get.call_count == 2
    assert (tmp_path / EXPORT_DIRECTORY / "articulo.txt").read_text(encoding="utf-8") == (
        "Árbol\n=====\n\nTexto enriquecido por IA.\n"
    )
    assert (
        f"Archivo guardado: {EXPORT_DIRECTORY / 'articulo.txt'}"
        in capsys.readouterr().out
    )


def test_main_exports_selected_enriched_text_as_pdf_and_still_exits(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    answers = ["Árbol", "Sí", "Enriquecida", "PDF", "articulo", "Salir"]
    install_questionary(monkeypatch, answers)

    with patch(
        "src.scraping.wikipedia_client.requests.get", return_value=SUCCESS_RESPONSE
    ):
        main()

    destination = tmp_path / EXPORT_DIRECTORY / "articulo.pdf"
    assert destination.read_bytes().startswith(b"%PDF")
    pdf_text = PdfReader(destination).pages[0].extract_text()
    assert "Árbol" in pdf_text
    assert ENRICHED_TEXT in pdf_text
    assert "Primer párrafo." not in pdf_text
    output = capsys.readouterr().out
    assert (
        f"Archivo guardado: {EXPORT_DIRECTORY / 'articulo.pdf'}" in output
    )
    assert output.endswith(EXIT_OUTPUT)


def test_main_replaces_an_existing_document_when_overwrite_is_confirmed(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / EXPORT_DIRECTORY / "articulo.txt"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("Versión anterior", encoding="utf-8")
    answers = ["Árbol", "Sí", "Original", "TXT", "articulo", "Sí", "Salir"]
    install_questionary(monkeypatch, answers)

    with patch(
        "src.scraping.wikipedia_client.requests.get", return_value=SUCCESS_RESPONSE
    ):
        main()

    saved = existing.read_text(encoding="utf-8")
    assert "Versión anterior" not in saved
    assert saved.startswith("Árbol\n=====")
    output = capsys.readouterr().out
    assert f"Archivo guardado: {EXPORT_DIRECTORY / 'articulo.txt'}" in output
    assert output.endswith(EXIT_OUTPUT)


def test_main_keeps_an_existing_document_when_overwrite_is_rejected(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / EXPORT_DIRECTORY / "articulo.txt"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("Versión anterior", encoding="utf-8")
    answers = [
        "Árbol", "Sí", "Original", "TXT", "articulo", "No", "otro", "Salir",
    ]
    install_questionary(monkeypatch, answers)

    with patch(
        "src.scraping.wikipedia_client.requests.get", return_value=SUCCESS_RESPONSE
    ):
        main()

    assert existing.read_text(encoding="utf-8") == "Versión anterior"
    assert (tmp_path / EXPORT_DIRECTORY / "otro.txt").exists()
    output = capsys.readouterr().out
    assert f"Archivo guardado: {EXPORT_DIRECTORY / 'otro.txt'}" in output
    assert output.endswith(EXIT_OUTPUT)


def test_main_allows_another_search_after_an_export_error(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    answers = [
        "Árbol", "Sí", "Original", "TXT", "articulo",
        "Buscar otro tema", "Música", "No", "Salir",
    ]
    install_questionary(monkeypatch, answers)

    with patch(
            "src.scraping.wikipedia_client.requests.get",
            side_effect=[SUCCESS_RESPONSE, SUCCESS_RESPONSE],
    ) as get, patch(
        "src.export.txt_exporter.TxtExporter.export",
        side_effect=PermissionError("sin permiso"),
    ):
        main()

    assert get.call_count == 2
    assert not (tmp_path / EXPORT_DIRECTORY / "articulo.txt").exists()
    output = capsys.readouterr().out
    assert (
        f"No se pudo guardar '{EXPORT_DIRECTORY / 'articulo.txt'}': sin permiso"
        in output
    )
    assert output.endswith(EXIT_OUTPUT)


def test_main_keeps_running_when_the_export_directory_cannot_be_created(
    monkeypatch, tmp_path, capsys, fake_ai_client
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / EXPORT_DIRECTORY).write_text("no es una carpeta", encoding="utf-8")
    answers = [
        "Árbol", "Sí", "Original", "TXT", "articulo",
        "Buscar otro tema", "Música", "No", "Salir",
    ]
    install_questionary(monkeypatch, answers)

    with patch(
        "src.scraping.wikipedia_client.requests.get",
        side_effect=[SUCCESS_RESPONSE, SUCCESS_RESPONSE],
    ) as get:
        main()

    assert get.call_count == 2
    output = capsys.readouterr().out
    assert f"No se pudo guardar '{EXPORT_DIRECTORY / 'articulo.txt'}'" in output
    assert output.endswith(EXIT_OUTPUT)