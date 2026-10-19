from pathlib import Path
from types import SimpleNamespace

import pytest
import questionary

from src.ui.export_destination_prompt import (
    EXPORT_DIRECTORY,
    NAME_PROMPT,
    NO_OPTION,
    OVERWRITE_PROMPT,
    YES_OPTION,
    ExportDestination,
    ExportDestinationPrompt,
)


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


@pytest.fixture
def existing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    file = tmp_path / EXPORT_DIRECTORY / "informe.txt"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("contenido original", encoding="utf-8")
    return file


def test_ask_accepts_an_existing_file_when_overwrite_is_confirmed(
    existing_file, monkeypatch, capsys
) -> None:
    prompts = install_questionary(monkeypatch, ["TXT", "informe", YES_OPTION])

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("txt", EXPORT_DIRECTORY / "informe.txt")
    assert prompts.messages[-1] == OVERWRITE_PROMPT.format(
        path=EXPORT_DIRECTORY / "informe.txt"
    )
    assert prompts.choices[-1] == [YES_OPTION, NO_OPTION]
    assert existing_file.read_text(encoding="utf-8") == "contenido original"
    assert capsys.readouterr().out == ""


def test_ask_asks_for_another_name_when_overwrite_is_rejected(
    existing_file, monkeypatch
) -> None:
    prompts = install_questionary(
        monkeypatch, ["TXT", "informe", NO_OPTION, "otro"]
    )

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("txt", EXPORT_DIRECTORY / "otro.txt")
    assert prompts.messages[-2:] == [
        OVERWRITE_PROMPT.format(path=EXPORT_DIRECTORY / "informe.txt"),
        NAME_PROMPT,
    ]
    assert existing_file.read_text(encoding="utf-8") == "contenido original"


def test_ask_does_not_ask_for_confirmation_when_the_file_does_not_exist(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    prompts = install_questionary(monkeypatch, ["PDF", "nuevo"])

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("pdf", EXPORT_DIRECTORY / "nuevo.pdf")
    assert len(prompts.messages) == 2
