"""Selecciona un idioma admitido para la traducción del artículo."""

import questionary

from src.translation.translation_service import TranslationService


class TranslationLanguagePrompt:
    """Pide un idioma de destino o permite omitir la traducción."""

    MENU_MESSAGE = "\n¿A qué idioma quieres traducir el contenido?"
    SKIP_LABEL = "Omitir traducción"

    def __init__(self, translation_service: TranslationService) -> None:
        self.translation_service = translation_service

    def ask(self) -> str | None:
        """Devuelve el código elegido; ``None`` indica que se omite."""
        languages = self.translation_service.get_supported_languages()

        choices = [
            questionary.Choice(f"{code} - {name}", code)
            for code, name in languages.items()
        ]
        choices.append(questionary.Choice(self.SKIP_LABEL))

        choice = questionary.select(self.MENU_MESSAGE, choices=choices).unsafe_ask()

        return None if choice == self.SKIP_LABEL else choice
