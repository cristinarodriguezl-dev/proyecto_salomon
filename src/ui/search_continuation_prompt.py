"""Prompt asking the user whether to run another search or exit."""

import questionary


class SearchContinuationPrompt:
    """Asks the user what to do after a search."""

    MENU_MESSAGE = "\n¿Qué quieres hacer ahora?"
    SEARCH_AGAIN_OPTION = "Buscar otro tema"
    EXIT_OPTION = "Salir"
    OPTIONS = [SEARCH_AGAIN_OPTION, EXIT_OPTION]

    def ask_search_again(self) -> bool:
        """Ask what to do next.

        Returns:
            True if the user wants another search, False if they want to exit.
        """
        choice = questionary.select(
            self.MENU_MESSAGE, choices=self.OPTIONS
        ).unsafe_ask()

        return choice == self.SEARCH_AGAIN_OPTION
