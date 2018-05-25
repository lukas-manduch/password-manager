"""Module containing main controller, which takes input as
dictionaries and maybe performs some actions over parts in core module
(like adding or removing entries).  Result returns also as
dictionary
"""

import constants
from core import PasswordFileManager
from core import KeyValueStore
from typing import List, Dict, Optional


class SessionController(object):
    """Class grouping main functionality of password manager.  Input
    should be passed to method process as dictionary.
    """

    def __init__(self, settings: dict) -> None:
        self.state = False # Valid or invalid state
        self.file_path = settings[constants.SETTINGS_FILE_PATH]
        self.pass_file: Optional[PasswordFileManager] = None
        self.store: Optional[KeyValueStore] = None
        self.indices: List[int] = list() # Found indices

    def update_status(self) -> dict:
        """Reinitialize self, try to read file create index and so on. Set
        value self.ok to either True or False and also return dictionary in
        format used by process method
        """
        self.state = True
        ret: Dict[str, str] = dict()
        try:
            if self.pass_file is None:
                self.pass_file = PasswordFileManager(self.file_path)

            self.store = KeyValueStore(self.pass_file)
            ret = {constants.RESPONSE: constants.RESPONSE_OK}
        except OSError as error:
            self.state = False
            ret = self.error_to_dict(str(error))
        return ret

    def process(self, data: dict) -> dict:
        """Process given command and return result as dictionary."""
        if not self.state:
            result = self.update_status()
            if not self.state:
                return result

        command = data.get(constants.COMMAND, "")
        # ADD
        if command is constants.COMMAND_ADD:
            key = data.get(constants.COMMAND_ADD_KEY, "")
            val = data.get(constants.COMMAND_ADD_VALUE, "")
            if not key or not val:
                return self.error_to_dict(constants.RESPONSE_ERROR_ARGUMENTS)
            return self.add(key, val)
        # SEARCH
        elif command is constants.COMMAND_SEARCH:
            return self.search(data.get(constants.COMMAND_SEARCH_VALUE, ""))
        # ERROR
        return self.error_to_dict(constants.RESPONSE_ERROR_UNKNOWN_COMMAND)

    def save_search_result(self, data: dict):
        """Save results from search command. They will be used by other
        commands, like delete, or show"""
        pass

    def search(self, search_pattern: str) -> dict:
        """Method representing command search"""
        assert self.store is not None
        assert self.pass_file is not None

        password_file_ref = self.pass_file # Hack for mypy
        self.indices = self.store.find_key(search_pattern)
        value_list = map(lambda x: password_file_ref[x], self.indices)
        value_dict = map(lambda x: {constants.SECRET_KEY: x[0],
                                    constants.SECRET_VALUE: x[1]},
                         value_list)
        return {constants.RESPONSE: constants.RESPONSE_OK,
                constants.RESPONSE_VALUES: list(value_dict)}

    def add(self, key: str, value: str) -> dict:
        """Append key and value to password file"""
        assert self.store is not None
        assert self.pass_file is not None
        assert self.state is True

        self.state = False # Force reload of key value store
        try:
            self.pass_file.append_entry(key, value)
        except OSError as error:
            return self.error_to_dict(str(error))
        return {constants.RESPONSE: constants.RESPONSE_OK}

    @staticmethod
    def error_to_dict(error_string: str) -> dict:
        """Return error in correct dict format"""
        return {constants.RESPONSE: constants.RESPONSE_ERROR,
                constants.RESPONSE_ERROR
                :str(error_string)}
