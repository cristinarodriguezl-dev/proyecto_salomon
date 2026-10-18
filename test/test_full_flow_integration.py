"""Prueba el recorrido completo sin consultar servicios externos."""

import json
from unittest.mock import patch

import requests

from src.main import main
from src.scraping.wikipedia_client import WIKIPEDIA_SEARCH_URL
from src.translation.translation_service import TranslationService


WIKIPEDIA_HTML = """
<html>
  <h1 id="firstHeading">Árbol</h1>
  <div id="mw-content-text">
    <div class="mw-parser-output">
      <p>Primer original.</p>
      <p>Segundo original.</p>
      <p>Tercer original.</p>
      <p>Cuarto original.</p>
      <p>Quinto original.</p>
    </div>
  </div>
</html>
"""
ENRICHED = "Primero ampliado.\n\nSegundo ampliado."
TRANSLATIONS = {
    "Primero ampliado.": "First enriched.",
    "Segundo ampliado.": "Second enriched.",
}


def _response(body: str) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response.encoding = "utf-8"
    response._content = body.encode("utf-8")
    return response


def test_search_enrich_translate_export_txt_and_exit_without_real_apis(
    monkeypatch, tmp_path, capsys
) -> None:
    """Comprueba el flujo real simulando solo las respuestas externas."""
    answers = iter(["Árbol", "n", "en", "s", "3", "txt", "article", "2"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    monkeypatch.chdir(tmp_path)

    def fake_get(url: str, **kwargs) -> requests.Response:
        if url == WIKIPEDIA_SEARCH_URL:
            assert kwargs["params"] == {"search": "Árbol"}
            return _response(WIKIPEDIA_HTML)

        if url == TranslationService.API_URL:
            assert kwargs["params"]["langpair"] == "es|en"
            paragraph = kwargs["params"]["q"]
            return _response(
                json.dumps(
                    {
                        "responseStatus": 200,
                        "responseData": {"translatedText": TRANSLATIONS[paragraph]},
                    }
                )
            )

        raise AssertionError(f"Petición inesperada: {url}")

    with (
        patch("requests.get", side_effect=fake_get) as http_get,
        patch("src.ai.ai_client.genai.Client") as gemini_client,
        patch("src.main.load_settings") as load_settings,
    ):
        load_settings.return_value.gemini_api_key = "fake-key"
        gemini_client.return_value.models.generate_content.return_value.text = ENRICHED

        main()

    load_settings.assert_called_once_with()
    gemini_client.assert_called_once_with(api_key="fake-key")
    generate_content = gemini_client.return_value.models.generate_content
    generate_content.assert_called_once()
    prompt = generate_content.call_args.kwargs["contents"]
    assert "Primer original." in prompt
    assert "Quinto original." in prompt
    assert http_get.call_count == 3

    output = capsys.readouterr().out
    assert "Árbol" in output
    assert "Primer original." in output
    assert ENRICHED in output
    assert "First enriched.\n\nSecond enriched." in output
    assert "Archivo guardado: article.txt" in output
    assert output.endswith("Programa finalizado.\n")

    exported = (tmp_path / "article.txt").read_text(encoding="utf-8")
    assert exported.startswith("Árbol\n")
    assert "First enriched.\n\nSecond enriched." in exported
    assert "Primero ampliado." not in exported
    assert "Primer original." not in exported
