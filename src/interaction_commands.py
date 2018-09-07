"""This module contains definitions of commands, which can be used by repl
defined in interaction
"""

# Disable no self use warning
# pylint: disable=R0201

import os
from textwrap import TextWrapper
from typing import Any, Dict, List, Tuple, Type

import constants
import interaction

COMMAND_MAP: Dict[str, Type[Any]] = dict()


class SearchInteractionCommand(interaction.InteractionCommand):
    """Class for handling user search on keys.  User can type search
    and pattern, or type search and hit return. Then propmt will show
    search mode and user will know that he is in search mode
    """
    COMMANDS = ['search', 'find']
    COMMAND_NAME = constants.COMMAND_SEARCH
    HELP = constants.HELP_SEARCH_COMMAND

    def __init__(self, verbose=True):
        super().__init__()
        self.verbose = verbose
        indent = ' '*2
        self.wrapper = TextWrapper(subsequent_indent=indent,
                                   max_lines=2, initial_indent=indent)

    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
        term = additional_input.get(constants.SEARCH_INTERACTION_PROMPT, "")

        if term == "":
            term = user_input.strip()

        if not term:
            raise interaction.InputNeeded(constants.SEARCH_INTERACTION_PROMPT,
                                          constants.SEARCH_INTERACTION_INFO)

        return {constants.COMMAND: constants.COMMAND_SEARCH,
                constants.COMMAND_SEARCH_VALUE: term}

    def call(self, *args, **kwargs) -> bool:
        """Format and print key,value pairs in args

        Values are printed only for first 2 matches.  Rest should be obtained
        by show command"""

        index = 0
        for index, entry in enumerate(args):
            print(str(index) + ". ", end="")
            print(entry[constants.SECRET_KEY])
            if index < 2:
                print("--------------------")
                for i in self.wrapper.wrap(entry[constants.SECRET_VALUE]):
                    print(i)
                print("--------------------")
        if index >= 2 and self.verbose:
            print()
            print(constants.HELP_SEARCH_MANY)
        return True


COMMAND_MAP["SearchInteractionCommand"] = SearchInteractionCommand

###########################################################################


class AddInteractionCommand(interaction.InteractionCommand):
    """Class for handling addition of entries.  User must enter keyword an
    then some text.  Keyword will be on one line and text must be finished
    by two empty lines
    """
    COMMANDS = ["add", "new"]
    COMMAND_NAME = constants.COMMAND_ADD
    HELP = constants.HELP_ADD_COMMAND

    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
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

    def call(self, *args, **kwargs) -> bool:
        """Just print ok / do nothing.

        Call is executed on response == ok so there is nothing to do """
        return True

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


COMMAND_MAP["AddInteractionCommand"] = AddInteractionCommand

###########################################################################


class DeleteInteractionCommand(interaction.InteractionCommand):
    """Delete command, deletes previous search results based on indices given"""
    COMMANDS = ['delete', 'remove']
    COMMAND_NAME = constants.COMMAND_DELETE

    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
        """Take as input indices which should be deleted.  Indices are for
        search list(something for which user already searched)"""
        indices: List[int] = interaction.parse_numbers(user_input)
        keyword_indices = additional_input.get(constants.COMMAND_DELETE_KEYWORD, "")
        indices.extend(interaction.parse_numbers(keyword_indices))

        if not indices:
            raise interaction.InputNeeded(constants.COMMAND_DELETE_KEYWORD,
                                          constants.COMMAND_DELETE_KEYWORD_HELP)

        return {constants.COMMAND: constants.COMMAND_DELETE,
                constants.COMMAND_DELETE_INDICES: indices}

    def call(self, *args, **kwargs) -> bool:
        """Just print ok / do nothing.

        Call is executed on response == ok so there is nothing to do"""
        return True

COMMAND_MAP["DeleteInteractionCommand"] = DeleteInteractionCommand

###########################################################################

class ViewInteractionCommand(interaction.InteractionCommand):
    """View secret command"""
    COMMANDS = ['view', 'show']
    COMMAND_NAME = constants.COMMAND_SHOW
    HELP = constants.HELP_SHOW_COMMAND

    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
        """Take input and find indices in it.  If there are not any,
        core will assume some default count."""
        indices = interaction.parse_numbers(user_input)
        ret: Dict[str, Any] = {constants.COMMAND: constants.COMMAND_SHOW}

        # If user entered indices, show only those
        if indices:
            ret[constants.COMMAND_SHOW_INDICES] = indices

        return ret

    def call(self, *args, **kwargs) -> bool:
        """Format and print key,value pairs in args

        Values are printed only for first 2 matches.  Rest should be obtained
        by show command"""

        for entry in args:
            key = entry.get(constants.SECRET_KEY, constants.RESPONSE_MISSING)
            value = entry.get(constants.SECRET_VALUE, constants.RESPONSE_MISSING)
            print("--- KEY ---")
            print(key)
            print("=== VALUE ===")
            print(value)
        return True

COMMAND_MAP["ViewInteractionCommand"] = ViewInteractionCommand

###########################################################################

class QuitInteractionCommand(interaction.InteractionCommand):
    """View secret command"""
    COMMANDS = ['quit', 'exit']
    COMMAND_NAME = constants.COMMAND_QUIT
    HELP = constants.HELP_QUIT_COMMAND

    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
        """Take whatever input eat all and return quit.

        """
        print("quitting")
        return {constants.COMMAND: constants.COMMAND_QUIT}


    def call(self, *args, **kwargs) -> bool:
        """Try to clear screen and return false"""
        self.cls()
        return False

    @staticmethod
    def cls() -> None:
        """Try to clear screen, so old output is deleted."""
        os.system('cls' if os.name == 'nt' else 'clear')

COMMAND_MAP["QuitInteractionCommand"] = QuitInteractionCommand
