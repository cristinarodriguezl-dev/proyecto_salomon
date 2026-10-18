"""Ask for a TXT or PDF filename without allowing filesystem paths."""

from dataclasses import dataclass
from pathlib import Path

VALID_FORMATS = {"txt", "pdf"}
INVALID_NAME_CHARACTERS = set('<>:"/\\|?*')
RESERVED_WINDOWS_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}

FORMAT_PROMPT = "Formato del archivo (TXT/PDF): "
NAME_PROMPT = "Nombre del archivo (sin ruta; extensión opcional): "
INVALID_FORMAT_MESSAGE = "Formato no válido. Escribe TXT o PDF."
EMPTY_NAME_MESSAGE = "El nombre del archivo no puede estar vacío."
INVALID_NAME_MESSAGE = (
    "Nombre no válido. Escribe solo un nombre de archivo, "
    "sin rutas ni caracteres especiales."
)
WRONG_EXTENSION_MESSAGE = (
    "La extensión del nombre debe coincidir con el formato elegido."
)
OVERWRITE_PROMPT = "El archivo '{path}' ya existe. ¿Quieres sobrescribirlo? (s/n): "
INVALID_ANSWER_MESSAGE = "Respuesta no válida. Escribe s o n."
YES_ANSWERS = {"s", "si", "sí"}
NO_ANSWERS = {"n", "no"}

@dataclass(frozen=True)
class ExportDestination:
    file_format: str
    path: Path

class ExportDestinationPrompt:
    def ask(self) -> ExportDestination:
        file_format = self._ask_format()

        while True:
            name = input(NAME_PROMPT).strip()

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
        while True:
            answer = input(OVERWRITE_PROMPT.format(path=path)).strip().casefold()

            if answer in YES_ANSWERS:
                return True
            if answer in NO_ANSWERS:
                return False

            print(INVALID_ANSWER_MESSAGE)

    @staticmethod
    def _ask_format() -> str:
        while True:
            file_format = input(FORMAT_PROMPT).strip().lower()

            if file_format in VALID_FORMATS:
                return file_format

            print(INVALID_FORMAT_MESSAGE)

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

        return Path(destination_name)