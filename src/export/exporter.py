"""Common contract for the classes that save a document in a file."""

from abc import ABC, abstractmethod
from pathlib import Path


class Exporter(ABC):
    """Interface that every output format (TXT, PDF) must implement."""

    @abstractmethod
    def export(self, title: str, content: str, destination: Path) -> None:
        """Save the title and the content in the file at the destination path."""