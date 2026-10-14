"""Prompt asking the user whether to run another search or exit."""


class SearchContinuationPrompt:
    """Asks the user what to do after a search and validates the answer."""

    SEARCH_AGAIN_OPTION = "1"
    EXIT_OPTION = "2"
    VALID_OPTIONS = {SEARCH_AGAIN_OPTION, EXIT_OPTION}

    def ask_search_again(self) -> bool:
        """Ask until a valid option is entered.

        Returns:
            True if the user wants another search, False if they want to exit.
        """
        while True:
            print("\n¿Qué quieres hacer ahora?")
            print("1. Buscar otro tema")
            print("2. Salir")
            option = input("Elige una opción (1/2): ").strip()

            if option in self.VALID_OPTIONS:
                return option == self.SEARCH_AGAIN_OPTION

            print("Opción no válida. Escribe 1 o 2.")