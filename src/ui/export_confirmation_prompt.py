"""Ask whether the user wants to save the displayed article."""


class ExportConfirmationPrompt:
    """Require an explicit yes or no before opening export choices."""

    def ask(self) -> bool:
        while True:
            answer = input("¿Quieres guardar el resultado? (s/n): ").strip().casefold()
            if answer in {"s", "sí", "si"}:
                return True
            if answer in {"n", "no"}:
                return False
            print("Respuesta no válida. Escribe s o n.")
