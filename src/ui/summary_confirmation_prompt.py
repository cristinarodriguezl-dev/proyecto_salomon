"""Ask whether the user wants a summary of the enriched content."""


class SummaryConfirmationPrompt:
    """Require an explicit yes or no before generating the summary."""

    def ask(self) -> bool:
        """Ask until the answer is valid and return True if the user wants it."""
        while True:
            answer = (
                input("¿Quieres resumir el contenido enriquecido? (s/n): ")
                .strip()
                .casefold()
            )
            if answer in {"s", "sí", "si"}:
                return True
            if answer in {"n", "no"}:
                return False
            print("Respuesta no válida. Escribe s o n.")
