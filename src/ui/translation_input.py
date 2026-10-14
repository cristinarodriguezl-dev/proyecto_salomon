"""Solicita al usuario el idioma de destino."""

LANGUAGES = {
    "1": ("Inglés", "en"),
    "2": ("Francés", "fr"),
    "3": ("Alemán", "de"),
    "4": ("Italiano", "it"),
    "5": ("Portugués", "pt"),
    "6": ("Español", "es"),
}


def request_target_language() -> tuple[str, str]:
    """Devuelve el nombre y el código del idioma seleccionado."""
    while True:
        print("\n¿A qué idioma deseas traducir el artículo?")

        for option, (name, _) in LANGUAGES.items():
            print(f"{option}. {name}")

        choice = input("Selecciona una opción: ").strip()

        if choice in LANGUAGES:
            return LANGUAGES[choice]

        print("Opción no válida. Inténtalo de nuevo.")
