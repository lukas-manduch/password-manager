"""Module containing main controller, which takes input as
dictionaries and maybe performs some actions over parts in core module
(like adding or removing entries).  Result returns also as
dictionary
"""

from typing import Any, List, Dict, Optional

import constants
from core import PasswordFileManager
from core import KeyValueStore


class SessionController(object):
    """Class grouping main functionality of password manager.  Input
    should be passed to method process as dictionary.
    """

    def __init__(self, settings: dict) -> None:
        self.state = False # Valid or invalid state
        self.file_path = settings[constants.SETTINGS_FILE_PATH]
        self.pass_file: Optional[PasswordFileManager] = None
        self.store: Optional[KeyValueStore] = None
        self.search_indices: List[int] = list() # Found indices

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
            self.search_indices.clear() # If there was some search now is invalid
            result = self.update_status()
            if not self.state:
                return result # Something went wrong

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
        # VIEW - SHOW
        elif command is constants.COMMAND_SHOW:
            indices = data.get(constants.COMMAND_SHOW_INDICES, None)
            return self.show(indices)
        # DELETE
        elif command is constants.COMMAND_DELETE:
            indices = data.get(constants.COMMAND_DELETE_INDICES, [])
            try:
                iter(indices)
                return self.delete(indices)
            except TypeError:
                return self.error_to_dict(constants.RESPONSE_ERROR_INVALID_ARGUMENT)

        # ERROR
        return self.error_to_dict(constants.RESPONSE_ERROR_UNKNOWN_COMMAND)

    def show(self, indices: Optional[List[int]] = None) -> Dict[str, Any]:
        """Return indices from search which already happened.  In INDICES
        you can specify which one you want to show. Default is all."""
        assert self.pass_file is not None

        if indices is None:
            indices = self.search_indices
        unique_indices = set(indices)
        if not unique_indices or max(unique_indices) > len(self.search_indices):
            return self.error_to_dict(constants.RESPONSE_ERROR_OUT_OF_RANGE)

        selected_indices = [self.search_indices[x] for x in unique_indices]
        password_file_ref = self.pass_file # Hack for mypy

        # Get key value pairs from password file
        value_list = map(lambda x: password_file_ref[x], selected_indices)
        # Form dict
        value_dict = map(lambda x: {constants.SECRET_KEY: x[0],
                                    constants.SECRET_VALUE: x[1]},
                         value_list)
        return {constants.RESPONSE: constants.RESPONSE_OK,
                constants.RESPONSE_VALUES: list(value_dict)}

    def search(self, search_pattern: str) -> dict:
        """Method representing command search. Usually called only from
        process"""
        assert self.store is not None
        assert self.pass_file is not None

        self.search_indices = self.store.find_key(search_pattern)
        return self.show()

    def add(self, key: str, value: str) -> dict:
        """Append key and value to password file. Called from process"""
        assert self.store is not None
        assert self.pass_file is not None
        assert self.state is True

        self.state = False # Force reload of key value store
        try:
            self.pass_file.append_entry(key, value)
            self.pass_file.save_contents()
        except OSError as error:
            return self.error_to_dict(str(error))
        return {constants.RESPONSE: constants.RESPONSE_OK}

    def delete(self, indices: List[int]) -> Dict[str, str]:
        """Delete entries specified in indices from file.  Indices
        are from previous search"""
        assert self.store is not None
        assert self.pass_file is not None
        assert self.state is True

        if not self.search_indices:
            return self.error_to_dict(constants.RESPONSE_ERROR_REQUIRES_SEARCH)
        if max(indices) >= len(self.search_indices):
            return self.error_to_dict(constants.RESPONSE_ERROR_OUT_OF_RANGE)

        self.state = False # Reload contents after delete

        try:
            delete_indices = map(lambda x: self.search_indices[x], set(indices))
            self.pass_file.delete_indices(list(delete_indices))
            self.pass_file.save_contents()
        except OSError:
            return self.error_to_dict(constants.RESPONSE_ERROR_UNKNOWN_ERROR)

        return {constants.RESPONSE: constants.RESPONSE_OK}

    @staticmethod
    def error_to_dict(error_string: str) -> dict:
        """Return error in correct dict format"""
        return {constants.RESPONSE: constants.RESPONSE_ERROR,
                constants.RESPONSE_ERROR
                :str(error_string)}
