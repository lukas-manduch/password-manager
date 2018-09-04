"""Module containing functions for user interaction with password
manager - parsing input displaying messages etc.
"""

# Disable unused argument warning
# pylint: disable=W0613
# Disable todo warning
# pylint: disable=W0511
# Disable no self use warning
# pylint: disable=R0201

import abc
from contextlib import suppress
import os
from pprint import pprint
from textwrap import TextWrapper
from typing import Any, Dict, List, Optional, Tuple, Type

import constants

COMMAND_MAP: Dict[str, Type[Any]] = dict()


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


class InteractionCommand(abc.ABC):
    """Base class for command parsers

    TODO: Neither of theese commands should be class. But I don't know
    what it should be :)
    """
    COMMANDS: List[str] = []  # list of keywords matching this command
    COMMAND_NAME: Optional[str] = None  # Unique identifier for this command
    HELP: Optional[str] = None  # Help message for command

    def __init__(self):
        pass

    @abc.abstractmethod
    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
        """Method for parsing user input.  USER_INPUT contains input eneterd
        by user (but command type is cut off), and ADDITIONAL_INPUT
        contains input collected by InputNeeded exceptions.

        Returns dict, if command is complete

        Throws InputNeeded if command is incomplete

        """
        pass

    def call(self, *args, **kwargs) -> bool:
        """Method called to process response from backend. Command is identified by
        command field in response, and values from response are passed as keyword
        arugments to this method"""
        for key, value in kwargs:
            print('--- ', end='')
            print(str(key), end='')
            print(' ---',)
            pprint(str(value))

        with suppress(TypeError):
            for item in iter(args):
                print("  " + str(item))
        return True

    @classmethod
    def create_empty(cls):
        """Return new command.  Protection against passing already instantiated
        command"""
        return cls()

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

    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
        description = constants.HELP_AMBIGUOUS + "\n" + "\n".join(self.commands)
        raise InputNeeded(key_description=description)

###########################################################################


class HelpInteractionCommand(InteractionCommand):
    """Purpose of this class is just react when somebody
    types help and show help to them
    """
    COMMANDS = ['help', '?']

    def __init__(self, help_str="?"):
        super().__init__()
        self.help = help_str

    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
        raise InputNeeded(key_description=self.help)

###########################################################################

class HelpMessageCommand(InteractionCommand):
    """This class is created by interactive session, when some error occurs and
    just prints error message"""

    def __init__(self, error_message="invalid request"):
        super().__init__()
        self.message: str = error_message

    def parse(self, user_input: str, additional_input: dict) -> Dict[str, Any]:
        raise NotImplementedError()

    def call(self, *args, **kwargs) -> bool:
        print("Error")
        print(str(self.message))
        print("----------------------")
        super().call(*args, **kwargs)
        return True
# This command is not in COMMAND_MAP

###########################################################################
# Rest of theese commands is implemented in interaction_commands.py,
# theese are only ones necessary for correct function of repl and process
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
        self.command_list: List[InteractionCommand] = self.instantiate_commands(function_list)
        help_command = help_from_commands(self.command_list)
        self.command_list.append(help_command)
        self.keyword = ""
        self.show_prompt = True
        self.show_help = True
        # TODO: Check for command name uniqueness
        # TODO: Generate help command

    def process(self, data: dict) -> dict:
        """Communication method for frontend.  Input and output is in json form"""
        response = data.get(constants.RESPONSE, constants.RESPONSE_MISSING)
        command = data.get(constants.COMMAND, constants.RESPONSE_MISSING)
        values = data.get(constants.RESPONSE_VALUES, {})
        #error = data.get(constants.RESPONSE_ERROR, "")

        if response is constants.RESPONSE_OK and command:
            command_instance = self.get_command(command)
            # Pass dict/list/int/str correctly
            if isinstance(values, dict):
                command_instance.call(**values)
            else:
                try:
                    command_instance.call(*values)
                except TypeError:
                    command_instance.call(values)
        else:
            print("Error")
        return {} # TODO


    def repl(self) -> dict:
        """GET command from user input and return it as dict. On
        KeyboardInterrupt cancel command, on another, rethrow"""
        user_input: str = ''
        additional_input: Dict[str, str] = dict()
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
        """Try to find one command whose COMMANDS, are most similar to
        argument.

        Returns command identified by ENTRY.  If some error happens (more
        commands with same length match, or no match at all), function will
        create its own help command which will only show error message.
        """
        matches = map(lambda x: get_best_match(entry, x.COMMANDS),
                      self.command_list)
        res = sorted(matches, reverse=True, key=lambda x: x[0])
        if not res or not res[0][0]:  # Command didn't match anythings
            return HelpInteractionCommand()
        # Check if we have only one match of this size
        res = list(filter(lambda x: x[0] == res[0][0], res))
        if len(res) > 1:
            return HelpAmbiguousInteractionCommand(list(map(lambda x: x[1],
                                                            res)))
        # Only one entry matches
        return self._find_command_by_keyword(res[0][1], self.command_list)

    def get_command(self, name: str) -> InteractionCommand:
        """Find command indentified by NAME in COMMAND_NAME.  If command
        doesn't exist, create error command and return it"""
        ret = list(filter(lambda x: x.COMMAND_NAME == name, self.command_list))
        if len(ret) == 1:
            return ret[0]
        return HelpMessageCommand("Critical error command not found")

    def get_input(self):
        """Function for getting user input"""
        prompt = ""
        if self.show_prompt:
            prompt = self.keyword + constants.PROMPT_SYMBOL
        return input(prompt).strip()

    @staticmethod
    def quit():
        """This method should be called before exitting, to clear console"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def _find_command_by_keyword(keyword: str,
                                 command_list: list) -> InteractionCommand:
        """"""
        ret = filter(lambda x: True if keyword in x.COMMANDS else False,
                     command_list)
        return next(ret)

    @staticmethod
    def remove_command_part(entry, command) -> str:
        """Find in command all his representations(COMMANDS), and remove from
        beginning of ENTRY part which represents one of these commands
        """
        return entry[get_best_match(entry, command.COMMANDS)[0]:]

    @staticmethod
    def instantiate_commands(command_list) -> List[InteractionCommand]:
        """Commands are expected to be passed as class names.  This method
        converts them to actual instances"""
        new_list = list()
        for command in command_list:
            new_list.append(command.create_empty())
        return new_list

    @staticmethod
    def error_from_dict(dict_response: Dict[str, Any]) -> HelpMessageCommand:
        """When response from backend is error, create Command which prints
        error message"""
        return HelpMessageCommand()
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

def get_best_match(search_for: str, search_in: list) -> Tuple[int, str]:
    """Given list of strings and one string to search for, returns length of
    longest match and entry with longest match as tuple. If there
    is match of size 0, function returns None
    """
    res = map(lambda x: (get_longest_match(x, search_for), x), search_in)
    try:
        return max(res, key=lambda x: x[0])
    except ValueError as _ve:
        return (0, '')

def parse_numbers(input_string: str) -> List[int]:
    """Given string with numbers, extract theese numbers,
    and return them as list of ints.

    Examples:
    1 2 ,3 --> [1, 2, 3]
    1,,23 4 --> [1, 23, 4]"""
    building_number = False
    current_number = ""
    return_digits = []
    for char in input_string:
        if char.isdigit():
            building_number = True
            current_number += char
        else:
            # If we just finished one number, append it
            if building_number:
                return_digits.append(int(current_number))
                building_number = False
                current_number = ""
            # else this is just some trash
    # Check for last number
    if building_number:
        return_digits.append(int(current_number))
    return return_digits

# Functions for formatting help

def help_from_commands(command_list: List[InteractionCommand]) -> HelpInteractionCommand:
    """Given list of loaded commands get their info and create one complete
    help message"""
    ret = ""
    indent = ' '*3
    wrapper = TextWrapper(subsequent_indent=indent, initial_indent=indent)
    ret = "\n".join(wrapper.wrap(constants.HELP_INTERACTION))
    ret += "\n"*2
    for command in command_list:
        names = ", ".join(command.COMMANDS)
        help_message = command.HELP or constants.RESPONSE_MISSING
        help_message = "\n".join(wrapper.wrap(help_message))
        ret += names + "\n" + help_message + "\n"*2
    return HelpInteractionCommand(ret)
