"""Ask for a TXT or PDF filename without allowing filesystem paths."""

from dataclasses import dataclass
from pathlib import Path

import questionary

EXPORT_DIRECTORY = Path("exports")
VALID_FORMATS = ("txt", "pdf")
INVALID_NAME_CHARACTERS = set('<>:"/\\|?*')
RESERVED_WINDOWS_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}

FORMAT_PROMPT = "Formato del archivo"
NAME_PROMPT = "Nombre del archivo (sin ruta; extensión opcional)"
EMPTY_NAME_MESSAGE = "El nombre del archivo no puede estar vacío."
INVALID_NAME_MESSAGE = (
    "Nombre no válido. Escribe solo un nombre de archivo, "
    "sin rutas ni caracteres especiales."
)
WRONG_EXTENSION_MESSAGE = (
    "La extensión del nombre debe coincidir con el formato elegido."
)
OVERWRITE_PROMPT = "El archivo '{path}' ya existe. ¿Quieres sobrescribirlo?"
YES_OPTION = "Sí"
NO_OPTION = "No"

@dataclass(frozen=True)
class ExportDestination:
    file_format: str
    path: Path

class ExportDestinationPrompt:
    def ask(self) -> ExportDestination:
        file_format = self._ask_format()

        while True:
            name = questionary.text(NAME_PROMPT).unsafe_ask().strip()

            try:
                path = self._build_path(name, file_format)
            except ValueError as error:
                print(error)
                continue

            if path.exists() and not self._confirm_overwrite(path):
                continue

            return ExportDestination(file_format=file_format, path=path)

    @staticmethod
    def _confirm_overwrite(path: Path) -> bool:
        answer = questionary.select(
            OVERWRITE_PROMPT.format(path=path), choices=[YES_OPTION, NO_OPTION]
        ).unsafe_ask()

        return answer == YES_OPTION

    @staticmethod
    def _ask_format() -> str:
        choices = [file_format.upper() for file_format in VALID_FORMATS]
        answer = questionary.select(FORMAT_PROMPT, choices=choices).unsafe_ask()

        return answer.lower()

    @staticmethod
    def _build_path(name: str, file_format: str) -> Path:
        if not name:
            raise ValueError(EMPTY_NAME_MESSAGE)

        if (
            name in {".", ".."}
            or name.casefold() in {".txt", ".pdf"}
            or name.endswith(".")
            or any(
                character in INVALID_NAME_CHARACTERS or ord(character) < 32
                for character in name
            )
        ):
            raise ValueError(INVALID_NAME_MESSAGE)

        suffix = Path(name).suffix.lower()
        if suffix in {".txt", ".pdf"}:
            if suffix != f".{file_format}":
                raise ValueError(WRONG_EXTENSION_MESSAGE)
            name = name[:-len(suffix)]

        destination_name = f"{name}.{file_format}"
        if (
            not name
            or name.endswith((".", " "))
            or name.split(".", 1)[0].upper() in RESERVED_WINDOWS_NAMES
            or len(destination_name) > 255
        ):
            raise ValueError(INVALID_NAME_MESSAGE)

        EXPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)

        return EXPORT_DIRECTORY / destination_name
