"""Module containing functions for user interaction with password
manager - parsing input displaying messages etc.
"""

from enum import Enum

import constants

class HelpInteractionCommand(InteractionCommand):
    def parse(self, user_input: str, additional_input: dict) -> dict:
        raise InputNeeded("", "Some help?")

class HelpAmbiguousInteractionCommand(InteractionCommand):
    def parse(self, user_input: str, additional_input: dict) -> dict:
        raise InputNeeded("", "Some help?")

class InteractionCommand(object):
    """Base class for command parsers

    TODO: Neither of theese commands should be class. But I don't know
    what it should be :)
    """
    COMMANDS = [] #list of keywords matching this command
    def __init__(self):
        pass

    def parse(self, user_input: str, additional_input: dict) -> dict:
        """Method for parsing user input.  USER_INPUT contains input eneterd
        by user (but command type is cut off), and ADDITIONAL_INPUT
        contains input collected by InputNeeded exceptions.

        Returns dict, if command is complete

        Throws InputNeeded if command is incomplete

        """
        return None


    def help(self) -> str:
        return "Help message"


class SearchInteractionCommand(InteractionCommand):
    COMMANDS = ['search', 'find']
    def parse(self, user_input: str, additional_input: dict) -> dict:
        term = additional_input.get(constants.SEARCH_INTERACTION_PROMPT, "")

        if term == "":
            term = user_input.strip()

        if len(term) == 0:
            raise  InputNeeded(constants.SEARCH_INTERACTION_PROMPT,
                            constants.SEARCH_INTERACTION_INFO)

        return {constants.COMMAND: constants.COMMAND_SEARCH,
                constants.COMMAND_SEARCH_VALUE: term}


class InputNeeded(Exception):
    def __init__(self, key_name, key_description):
        super().__init__()
        self.key_name = key_name
        self.key_description = key_description

COMMANDS_LIST = [SearchInteractionCommand]

###########################################
##############  METHODS  ##################
###########################################



def _get_longest_match(search_for: str, search_in: str):
    """Look for SEARCH_FOR in beginning of SEARCH_IN.
    Returns length of match
    """
    search_for = str(search_for).casefold()
    search_in = str(search_in).casefold()
    length = min(len(search_in), len(search_for))
    for i in range(length):
        if search_for[i] != search_in[i]:
            return i
    return length
