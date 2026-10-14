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


@dataclass(frozen=True)
class ExportDestination:
    """The selected format and relative path for a future export."""

    file_format: str
    path: Path


class ExportDestinationPrompt:
    """Ask again until the format and filename form a valid destination."""

    def ask(self) -> ExportDestination:
        """Return a valid choice without creating or overwriting a file."""
        file_format = self._ask_format()

        while True:
            name = input(NAME_PROMPT).strip()

            try:
                path = self._build_path(name, file_format)
            except ValueError as error:
                print(error)
                continue

            return ExportDestination(file_format=file_format, path=path)

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
