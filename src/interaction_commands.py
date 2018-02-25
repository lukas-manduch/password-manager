"""This module"""
import constants
import interaction


class SearchInteractionCommand(interaction.InteractionCommand):
    COMMANDS = ['search', 'find']

    def parse(self, user_input: str, additional_input: dict) -> dict:
        term = additional_input.get(constants.SEARCH_INTERACTION_PROMPT, "")

        if term == "":
            term = user_input.strip()

        if len(term) == 0:
            raise interaction.InputNeeded(constants.SEARCH_INTERACTION_PROMPT,
                              constants.SEARCH_INTERACTION_INFO)

        return {constants.COMMAND: constants.COMMAND_SEARCH,
                constants.COMMAND_SEARCH_VALUE: term}

###########################################################################


class DeleteInteractionCommand(interaction.InteractionCommand):
    COMMANDS = ['delete', 'remove']

###########################################################################


class ViewInteractionCommand(interaction.InteractionCommand):
    COMMANDS = ['view', 'show']
