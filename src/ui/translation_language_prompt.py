"""Selecciona un idioma admitido para la traducción del artículo."""

from src.translation.translation_service import TranslationService


class TranslationLanguagePrompt:
    """Pide un idioma de destino o permite omitir la traducción."""

    SKIP_OPTION = "0"

    def __init__(self, translation_service: TranslationService) -> None:
        self.translation_service = translation_service

    def ask(self) -> str | None:
        """Devuelve el código elegido; ``None`` indica que se omite."""
        languages = self.translation_service.get_supported_languages()

        while True:
            print("\n¿A qué idioma quieres traducir el contenido?")
            for code, name in languages.items():
                print(f"{code} - {name}")
            print(f"{self.SKIP_OPTION} - Omitir traducción")

            choice = input("Escribe el código o nombre del idioma: ").strip().casefold()
            if choice == self.SKIP_OPTION:
                return None

            for code, name in languages.items():
                if choice in (code.casefold(), name.casefold()):
                    return code

            print(
                "Idioma no admitido. Elige uno de los idiomas mostrados "
                "o 0 para omitir la traducción."
            )
