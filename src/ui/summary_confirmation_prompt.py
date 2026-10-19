"""Ask whether the user wants a summary of the enriched content."""

import questionary

PROMPT_MESSAGE = "¿Quieres resumir el contenido enriquecido?"
YES_OPTION = "Sí"
NO_OPTION = "No"
OPTIONS = [YES_OPTION, NO_OPTION]


class SummaryConfirmationPrompt:
    """Require an explicit yes or no before generating the summary."""

    def ask(self) -> bool:
        """Return True if the user wants the summary."""
        answer = questionary.select(PROMPT_MESSAGE, choices=OPTIONS).unsafe_ask()

        return answer == YES_OPTION
