"""Module containing functions for user interaction with password
manager - parsing input displaying messages etc.
"""

from enum import Enum

import constants


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
        return {}


    def help(self) -> str:
        return "Help message"

    def remove_command_part(self, entry) -> str:
        return entry[get_best_match(entry, self.COMMANDS)[0]:]

###########################################################################


class HelpInteractionCommand(InteractionCommand):
    COMMANDS = ['help']
    def parse(self, user_input: str, additional_input: dict) -> dict:
        raise InputNeeded(key_description="Some help?")

###########################################################################

class HelpAmbiguousInteractionCommand(InteractionCommand):
    def __init__(self, command_list):
        self.commands = command_list

    def parse(self, user_input: str, additional_input: dict) -> dict:
        description = constants.HELP_AMBIGUOUS + "{}".format(self.commands)
        raise InputNeeded(key_description=description)

###########################################################################

class InputNeeded(Exception):
    def __init__(self, key_name='', key_description='', reset=False):
        self.key_name = key_name
        self.key_description = key_description

###########################################################################


class SearchInteractionCommand(InteractionCommand):
    COMMANDS = ['search', 'find']
    def parse(self, user_input: str, additional_input: dict) -> dict:
        user_input = self.remove_command_part(user_input)
        term = additional_input.get(constants.SEARCH_INTERACTION_PROMPT, "")

        if term == "":
            term = user_input.strip()

        if len(term) == 0:
            raise InputNeeded(constants.SEARCH_INTERACTION_PROMPT,
                            constants.SEARCH_INTERACTION_INFO)

        return {constants.COMMAND: constants.COMMAND_SEARCH,
                constants.COMMAND_SEARCH_VALUE: term}

###########################################################################


class DeleteInteractionCommand(InteractionCommand):
    COMMANDS = ['delete', 'remove']

###########################################################################


class ViewInteractionCommand(InteractionCommand):
    COMMANDS = ['view', 'show']


###########################################################################
class InteractiveSession:
    """This class is responsible for interaction with user and parsing
    current command.  After identifying correct parser, parsing of
    input is done by objects passed to initializer.

    Theese parsers can return dict, with parsed response which will be
    propagated to main program, or throw InputNeeded exception, which
    tells this class what should it ask from user.
    """

    def __init__(self, function_list):
        self.command_list = function_list
        self.keyword = ""
        self.show_prompt = True
        self.show_help = True


    def repl(self) -> dict:
        """Get command from user input and return it as dict"""
        additional_input = {}
        user_input = ''
        while(True):
            inp = self.get_input()

            if len(self.keyword) == 0:
                user_input = inp
                additional_input = {}
            else:
                additional_input[self.keyword] = inp

            command = self.find_command(user_input)
            try:
                return command.parse(user_input,
                                     additional_input)
            except InputNeeded as inpn:
                if self.show_help:
                    print(inpn.key_description)
                self.keyword = inpn.key_name


    def find_command(self, entry: str) -> InteractionCommand:
        """Returns one command which is identified by entry. If some error
        happens fucntion should create its own help command which will only
        show help or error message.
        """
        res = map(lambda x: get_best_match(entry, x.COMMANDS), self.command_list)
        res = sorted(res, reverse=True, key=lambda x: x[0])
        if len(res) == 0 or res[0][0] == 0: # Command didn't match anythings
            return HelpInteractionCommand()
        # Check if we have only one match ot this size
        res = list(filter(lambda x: x[0] == res[0][0], res))
        if len(res) > 1:
            return HelpAmbiguousInteractionCommand(list(map(lambda x: x[1], res)))
        # Only one entry matches
        return self._find_command_by_keyword(res[0][1], self.command_list)()

    @staticmethod
    def _find_command_by_keyword(keyword, command_list) -> list:
        ret = filter(lambda x: True if keyword in x.COMMANDS else False , command_list)
        return next(ret)

    def get_input(self):
        """Function for getting user input"""
        prompt = ""
        if self.show_prompt:
            prompt = self.keyword + constants.PROMPT_SYMBOL
        return input(prompt).strip()

###########################################################################

COMMANDS_LIST = [SearchInteractionCommand,
                 HelpInteractionCommand,
                 DeleteInteractionCommand,
                 ViewInteractionCommand]

###########################################
##############  METHODS  ##################
###########################################



def get_longest_match(search_for: str, search_in: str):
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

def get_best_match(search_for: str, search_in: list()) -> (int, str):
    """Given list of strings and one string to search for, returns length of
    longest match and entry with longest match as tuple. If there
    is match of size 0, function returns None
    """
    res = map(lambda x: (get_longest_match(x, search_for), x), search_in)
    try:
        return max(res, key=lambda x: x[0])
    except ValueError as ve:
        return (0, '')
