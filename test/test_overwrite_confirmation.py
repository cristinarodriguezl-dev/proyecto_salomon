from pathlib import Path
from unittest.mock import Mock

import pytest

from src.ui.export_destination_prompt import (
    INVALID_ANSWER_MESSAGE,
    NAME_PROMPT,
    OVERWRITE_PROMPT,
    ExportDestination,
    ExportDestinationPrompt,
)

@pytest.fixture
def existing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    file = tmp_path / "informe.txt"
    file.write_text("contenido original", encoding="utf-8")
    return file

@pytest.mark.parametrize("answer", ["s", "S", " sí ", "si", "SI"])
def test_ask_accepts_an_existing_file_when_overwrite_is_confirmed(
    answer, existing_file, monkeypatch, capsys
) -> None:
    fake_input = Mock(side_effect=["txt", "informe", answer])
    monkeypatch.setattr("builtins.input", fake_input)

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("txt", Path("informe.txt"))
    assert fake_input.call_args_list[-1].args[0] == OVERWRITE_PROMPT.format(
        path=Path("informe.txt")
    )
    assert existing_file.read_text(encoding="utf-8") == "contenido original"
    assert capsys.readouterr().out == ""

@pytest.mark.parametrize("answer", ["n", "N", " no ", "NO"])
def test_ask_asks_for_another_name_when_overwrite_is_rejected(
    answer, existing_file, monkeypatch
) -> None:
    fake_input = Mock(side_effect=["txt", "informe", answer, "otro"])
    monkeypatch.setattr("builtins.input", fake_input)

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("txt", Path("otro.txt"))
    assert [call.args[0] for call in fake_input.call_args_list][-2:] == [
        OVERWRITE_PROMPT.format(path=Path("informe.txt")),
        NAME_PROMPT,
    ]
    assert existing_file.read_text(encoding="utf-8") == "contenido original"

def test_ask_repeats_the_question_after_an_invalid_answer(
    existing_file, monkeypatch, capsys
) -> None:
    fake_input = Mock(side_effect=["txt", "informe", "quizá", "", "s"])
    monkeypatch.setattr("builtins.input", fake_input)

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("txt", Path("informe.txt"))
    assert capsys.readouterr().out == f"{INVALID_ANSWER_MESSAGE}\n" * 2

def test_ask_does_not_ask_for_confirmation_when_the_file_does_not_exist(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    fake_input = Mock(side_effect=["pdf", "nuevo"])
    monkeypatch.setattr("builtins.input", fake_input)

    result = ExportDestinationPrompt().ask()

    assert result == ExportDestination("pdf", Path("nuevo.pdf"))
    assert fake_input.call_count == 2