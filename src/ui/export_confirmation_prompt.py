"""Ask whether the user wants to save the displayed article."""

import questionary

PROMPT_MESSAGE = "¿Quieres guardar el resultado?"
YES_OPTION = "Sí"
NO_OPTION = "No"
OPTIONS = [YES_OPTION, NO_OPTION]


class ExportConfirmationPrompt:
    """Require an explicit yes or no before opening export choices."""

    def ask(self) -> bool:
        """Return True if the user wants to save the article."""
        answer = questionary.select(PROMPT_MESSAGE, choices=OPTIONS).unsafe_ask()

        return answer == YES_OPTION
