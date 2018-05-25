"""Module containing functions for user interaction with password
manager - parsing input displaying messages etc.
"""
import constants

# Disable unused argument warning
# pylint: disable=W0613
class InputNeeded(Exception):
    """This class can be thrown by interaction commands.  Class forces repl
    loop to show prompt with KEY_NAME and shows help as KEY_DESCRIPTION.  Next
    time command is called, user input is in map passed to parse function as
    second argument, under key KEY_NAME"""

    def __init__(self, key_name='', key_description=''):
        super().__init__()
        self.key_name = key_name
        self.key_description = key_description

###########################################################################


class InteractionCommand(object):
    """Base class for command parsers

    TODO: Neither of theese commands should be class. But I don't know
    what it should be :)
    """
    COMMANDS = []  # list of keywords matching this command

    def __init__(self):
        pass

    @staticmethod
    def parse(user_input: str, additional_input: dict) -> dict:
        """Method for parsing user input.  USER_INPUT contains input eneterd
        by user (but command type is cut off), and ADDITIONAL_INPUT
        contains input collected by InputNeeded exceptions.

        Returns dict, if command is complete

        Throws InputNeeded if command is incomplete

        """
        return {}

    @staticmethod
    def help() -> str:
        """Return help message"""
        return "Help message"

###########################################################################


class HelpAmbiguousInteractionCommand(InteractionCommand):
    """This class is used when more than one class has commands which match
    by exactly same length.  Purpose of this class is to inform user about
    this and show commands which he might want
    """
    def __init__(self, command_list):
        super().__init__()
        self.commands = command_list

    def parse(self, user_input: str, additional_input: dict) -> dict:
        description = constants.HELP_AMBIGUOUS + "{}".format(self.commands)
        raise InputNeeded(key_description=description)

###########################################################################


class HelpInteractionCommand(InteractionCommand):
    """Purpose of this class is just react when somebody
    types help and show help to them
    """
    COMMANDS = ['help', '?']

    def parse(self, user_input: str, additional_input: dict) -> dict:
        raise InputNeeded(key_description="Some help?")

###########################################################################
# Rest of theese commands is implemented in interaction_commands.py,
# theese are only ones necessary for correct function of repl
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
        """GET command from user input and return it as dict. On
        KeyboardInterrupt cancel command, on another, rethrow"""
        user_input, additional_input = '', dict()
        self.keyword = ""
        while True:
            try:
                inp = self.get_input()
            except KeyboardInterrupt: # Jump out from command, or quit
                if self.keyword: # If command is active, cancel it
                    user_input, additional_input, self.keyword = "", {}, ""
                    print()
                    continue
                raise
            # If keyword is set this is InputNeeded exception
            if not self.keyword:
                user_input, additional_input = inp, {}
            else:
                additional_input[self.keyword] = inp
            # Parse input
            command = self.find_command(user_input)
            try:
                return command.parse(self.remove_command_part(user_input, command),
                                     additional_input)

            except InputNeeded as inpn:
                self.keyword = inpn.key_name
                if self.show_help and inpn.key_description:
                    print(inpn.key_description)

    def find_command(self, entry: str) -> InteractionCommand:
        """Returns one command which is identified by entry. If some error
        happens fucntion should create its own help command which will only
        show help or error message.
        """
        res = map(lambda x: get_best_match(entry, x.COMMANDS),
                  self.command_list)
        res = sorted(res, reverse=True, key=lambda x: x[0])
        if not res or not res[0][0]:  # Command didn't match anythings
            return HelpInteractionCommand()
        # Check if we have only one match of this size
        res = list(filter(lambda x: x[0] == res[0][0], res))
        if len(res) > 1:
            return HelpAmbiguousInteractionCommand(list(map(lambda x: x[1],
                                                            res)))
        # Only one entry matches
        return self._find_command_by_keyword(res[0][1], self.command_list)()

    def get_input(self):
        """Function for getting user input"""
        prompt = ""
        if self.show_prompt:
            prompt = self.keyword + constants.PROMPT_SYMBOL
        return input(prompt).strip()

    @staticmethod
    def _find_command_by_keyword(keyword: str,
                                 command_list: list) -> InteractionCommand:
        ret = filter(lambda x: True if keyword in x.COMMANDS else False,
                     command_list)
        return next(ret)

    @staticmethod
    def remove_command_part(entry, command) -> str:
        """Find in command all his representations(COMMANDS), and remove from
        beginning of ENTRY part which represents one of these commands
        """
        return entry[get_best_match(entry, command.COMMANDS)[0]:]

###########################################################################

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

def get_best_match(search_for: str, search_in: list) -> (int, str):
    """Given list of strings and one string to search for, returns length of
    longest match and entry with longest match as tuple. If there
    is match of size 0, function returns None
    """
    res = map(lambda x: (get_longest_match(x, search_for), x), search_in)
    try:
        return max(res, key=lambda x: x[0])
    except ValueError as _ve:
        return (0, '')
