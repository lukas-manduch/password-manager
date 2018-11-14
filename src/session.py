"""Module containing main controller, which takes input as
dictionaries and maybe performs some actions over parts in core module
(like adding or removing entries).  Result returns also as
dictionary

Calls:
 Add
 Search
 View
 Show
 Delete
 Stats
"""

from typing import Any, List, Dict, Optional

import constants
from core import PasswordFileManager
from core import KeyValueStore


class SessionController:
    """Class grouping main functionality of password manager.  Input should be
    passed to method process as dictionary.

    Variables:
     search_indices - Indices from last search, specifying best matches [0] is
     best.  Count is specified as argument to search"""

    def __init__(self, settings: dict) -> None:
        self.state = False # Valid or invalid state
        self.file_path = settings[constants.SETTINGS_FILE_PATH]
        self.password = settings[constants.SETTINGS_PASSWORD]
        self.pass_file: Optional[PasswordFileManager] = None
        self.store: Optional[KeyValueStore] = None
        self.search_indices: List[int] = list() # Found indices

    def update_status(self) -> str:
        """Reinitialize self, try to read file create index and so on.  Set
        value self.ok to either True or False and also return error message"""
        self.state = True
        ret = ""
        try:
            if self.pass_file is None:
                self.pass_file = PasswordFileManager(self.file_path, self.password)
            self.store = KeyValueStore(self.pass_file)
        except OSError as error:
            self.state = False
            ret = str(error)
        return ret

    def process(self, data: dict) -> dict:
        """Process given command and return result as dictionary."""
        if not self.state:
            self.search_indices.clear() # If there was some search now is invalid
            result = self.update_status()
            if not self.state:
                return self.error_to_dict(result)

        command = data.get(constants.COMMAND, "")
        ret = self.error_to_dict(constants.RESPONSE_ERROR_UNKNOWN_COMMAND)
        # ADD
        if command is constants.COMMAND_ADD:
            key = data.get(constants.COMMAND_ADD_KEY, "")
            val = data.get(constants.COMMAND_ADD_VALUE, "")
            if not key or not val:
                ret = self.error_to_dict(constants.RESPONSE_ERROR_ARGUMENTS)
            else:
                ret = self.add(key, val)
        # SEARCH
        elif command is constants.COMMAND_SEARCH:
            ret = self.search(data.get(constants.COMMAND_SEARCH_VALUE, ""))
        # VIEW - SHOW
        elif command is constants.COMMAND_SHOW:
            indices = data.get(constants.COMMAND_SHOW_INDICES, None)
            ret = self.show(indices)
        # DELETE
        elif command is constants.COMMAND_DELETE:
            indices = data.get(constants.COMMAND_DELETE_INDICES, [])
            try:
                iter(indices)
                ret = self.delete(indices)
            except TypeError:
                ret = self.error_to_dict(constants.RESPONSE_ERROR_INVALID_ARGUMENT)
        # STATS
        elif command is constants.COMMAND_STATS:
            ret = self.stats()
        # QUIT
        elif command is constants.COMMAND_QUIT:
            ret = self.quit()

        return ret

    def show(self, indices: Optional[List[int]] = None) -> Dict[str, Any]:
        """Return indices from search which already happened.  In INDICES
        you can specify which one you want to show. Default is all."""
        assert self.pass_file is not None

        if indices is None: # Show all matches
            indices = list(range(len(self.search_indices)))
        unique_indices = set(indices)

        if not unique_indices or max(unique_indices) >= len(self.search_indices):
            return self.error_to_dict(constants.RESPONSE_ERROR_OUT_OF_RANGE)

        selected_indices = [self.search_indices[x] for x in unique_indices]
        password_file_ref = self.pass_file # Hack for mypy

        # Get key value pairs from password file
        value_list = map(lambda x: password_file_ref[x], selected_indices)
        # Tuples to dict
        value_dict = map(lambda x: {constants.SECRET_KEY: x[0],
                                    constants.SECRET_VALUE: x[1]},
                         value_list)
        return self.ok_to_dict(constants.COMMAND_SHOW, list(value_dict))

    def search(self, search_pattern: str) -> dict:
        """Method representing command search. Usually called only from
        process"""
        assert self.store is not None
        assert self.pass_file is not None

        self.search_indices = self.store.find_key(search_pattern)
        ret_dict = self.show()
        ret_dict[constants.COMMAND] = constants.COMMAND_SEARCH
        return ret_dict

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
        return self.ok_to_dict(constants.COMMAND_ADD)

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

        return self.ok_to_dict(constants.COMMAND_DELETE)

    def stats(self):
        """Command for getting stats for this session, like number of
        entries, success rate and so on"""
        ret: Dict[str, Any] = dict()
        ret[constants.RESPONSE_STATS_STATUS] = constants.RESPONSE_ERROR
        ret[constants.RESPONSE_STATS_DECRYPTION_RATE] = 0
        if self.state: # This is always true when called from process
            ret[constants.RESPONSE_STATS_STATUS] = constants.RESPONSE_OK
            ret[constants.RESPONSE_STATS_DECRYPTION_RATE] = self.pass_file.success
        return self.ok_to_dict(constants.COMMAND_STATS, ret)

    def quit(self):
        """For now do nothing just return ok.  Later we can do some
        cleanups/backups. """
        return self.ok_to_dict(constants.COMMAND_QUIT)

    @staticmethod
    def error_to_dict(error_string: str) -> dict:
        """Return error in correct dict format"""
        return {constants.RESPONSE: constants.RESPONSE_ERROR,
                constants.RESPONSE_ERROR
                :str(error_string)}

    @staticmethod
    def ok_to_dict(original_command: str, value=None) -> Dict[str, Any]:
        """Return ok response in correct format"""
        ret = {constants.RESPONSE: constants.RESPONSE_OK,
               constants.COMMAND: str(original_command)}
        if value:
            ret[constants.RESPONSE_VALUES] = value
        return ret
