"""This module contains definitions of commands, which can be used by repl
defined in interaction
"""
from typing import List, Tuple

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


class AddInteractionCommand(interaction.InteractionCommand):
    """Class for handling addition of entries.  User must enter keyword an
    then some text.  Keyword will be on one line and text must be finished
    by two empty lines
    """
    COMMANDS = ["add"]
    def parse(self, user_input: str, additional_input: dict) -> dict:
        term, value = "", ""
        # Get key
        term = additional_input.get(constants.COMMAND_ADD_KEY, "")
        if not term:
            term, value = self.parse_input_line(user_input.strip())
            if not term:
                raise interaction.InputNeeded(constants.COMMAND_ADD_KEY,
                                              constants.ADD_INTERACTION_KEY_MISSING)
        # Get value
        if not value:
            current_value = self.value_to_list(additional_input)
            # Check if value ends with two empty lines
            value = self.get_value_or_raise(current_value)

        return {constants.COMMAND: constants.COMMAND_ADD,
                constants.COMMAND_ADD_KEY: term,
                constants.COMMAND_ADD_VALUE: value}


    @staticmethod
    def value_to_list(additional_input: dict) -> list:
        """Transform all entries with keys as '1' '2' and so on, to list"""
        i = 1
        result: List[str] = list()
        while True:
            if str(i) not in additional_input:
                return result
            result.append(additional_input[str(i)])
            i += 1

    @staticmethod
    def get_value_or_raise(value_list: list) -> str:
        """If last two lines are not empty, raise input needed"""
        if len(value_list) < 2 or "".join(value_list[-2:]):
            raise interaction.InputNeeded(key_name=str(len(value_list) + 1))
        return "\n".join(value_list)

    @staticmethod
    def parse_input_line(line: str) -> Tuple[str, str]:
        """Split string at first whitespace to two"""
        parts = line.split(maxsplit=1)
        parts.extend(["", ""])
        return (parts[0], parts[1])


###########################################################################


class DeleteInteractionCommand(interaction.InteractionCommand):
    """Delete command"""
    COMMANDS = ['delete', 'remove']

###########################################################################


class ViewInteractionCommand(interaction.InteractionCommand):
    """View secret command"""
    COMMANDS = ['view', 'show']
