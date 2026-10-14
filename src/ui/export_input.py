"""Solicita el formato de exportación al usuario."""


def request_export_format() -> str:
    """Devuelve el formato seleccionado: txt o pdf."""
    while True:
        print("\n¿En qué formato deseas guardar el artículo?")
        print("1. TXT")
        print("2. PDF")

        choice = input("Selecciona una opción: ").strip()

        if choice == "1":
            return "txt"

        if choice == "2":
            return "pdf"

        print("Opción no válida. Selecciona 1 o 2.")
