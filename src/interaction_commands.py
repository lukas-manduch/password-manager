"""This module contains definitions of commands, which can be used by repl
defined in interaction
"""
import constants
import interaction


class SearchInteractionCommand(interaction.InteractionCommand):
    """Class for handling user search on keys.  User can type search
    and pattern, or type search and hit return. Then propmt will show
    search mode and user will know that he is in search mode
    """
    COMMANDS = ['search', 'find']

    def parse(self, user_input: str, additional_input: dict) -> dict:
        term = additional_input.get(constants.SEARCH_INTERACTION_PROMPT, "")

        if term == "":
            term = user_input.strip()

        if not term:
            raise interaction.InputNeeded(constants.SEARCH_INTERACTION_PROMPT,
                                          constants.SEARCH_INTERACTION_INFO)

        return {constants.COMMAND: constants.COMMAND_SEARCH,
                constants.COMMAND_SEARCH_VALUE: term}

###########################################################################


class DeleteInteractionCommand(interaction.InteractionCommand):
    """Delete command"""
    COMMANDS = ['delete', 'remove']

###########################################################################


class ViewInteractionCommand(interaction.InteractionCommand):
    """View secret command"""
    COMMANDS = ['view', 'show']
