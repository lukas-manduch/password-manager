"""Module containing helper functions"""
import argparse
import getpass
import os
from typing import Any, Dict

import constants
import interaction
import session

# Disable unused argument warning
# pylint: disable=W0613

class Module:
    """Convenience wrapper for modules (frontend and backend)"""
    def __init__(self, module: Any) -> None:
        self.module = module

    def is_loaded(self):
        """True if module is already set"""
        return self.module is not None

    def process(self, *args):
        """Call module process"""
        if self.module:
            return self.module.process(*args)
        return {constants.RESPONSE: constants.RESPONSE_ERROR}


################################################################################
################################ INIT FUNCTIONS ################################
################################################################################

# If one of these functions returns False, whole app stops with error.
# In future, they will have possibilty to

def parse_arguments(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """Parse program arguments and set them in SETTINGS"""
    parser = argparse.ArgumentParser(prog=constants.PROGRAM_NAME)
    parser.add_argument(constants.ARG_PASSOWRD_SHORT, constants.ARG_PASSOWRD,
                        help=constants.ARG_PASSOWRD_DESCRIPTION, type=str, dest='password')
    parser.add_argument(constants.ARG_FILEPATH, constants.ARG_FILEPATH_SHORT,
                        help=constants.ARG_FILEPATH_DESCRIPTION, type=str, dest='path')
    args = parser.parse_args()

    if args.password:
        settings[constants.SETTINGS_PASSWORD] = args.password
    if args.path:
        settings[constants.SETTINGS_FILE_PATH] = args.path
    return True

def set_settings(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """Merge default and parameter settings"""
    new_settings = constants.DEFAULT_SETTINGS
    new_settings.update(settings)
    settings.update(new_settings)
    # Change path to absolute
    if not constants.SETTINGS_FILE_PATH in settings:
        return False
    given_path = os.path.expanduser(settings[constants.SETTINGS_FILE_PATH])
    settings[constants.SETTINGS_FILE_PATH] = os.path.abspath(given_path)
    return True

def load_frontend(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """Based on settings decide which frontends to load.  For now always
    load ineraction"""
    text_command_list = settings.get(constants.SETTINGS_INTERACTION_COMMANDS_LIST, list())
    # Tranform strings to classes
    import interaction_commands
    command_list = []

    class_map = dict()
    class_map.update(interaction_commands.COMMAND_MAP)
    class_map.update(interaction.COMMAND_MAP)

    for command in text_command_list:
        if command in class_map:
            command_list.append(class_map[command])

    frontend.module = interaction.InteractiveSession(command_list)
    return True

def load_backend(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """Just load backend. If password is not already in settings, return False."""
    assert constants.SETTINGS_FILE_PATH in settings
    assert constants.SETTINGS_PASSWORD in settings

    if constants.SETTINGS_PASSWORD not in settings:
        return False
    controller = session.SessionController(settings)
    backend.module = controller
    return True


def create_password_file(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """If file and path defined in settings doesn't exist, create it.
    Also check for permissions on file."""
    if constants.SETTINGS_FILE_PATH not in settings:
        return False
    given_path = settings[constants.SETTINGS_FILE_PATH]
    # Path cannot be dir already
    if os.path.exists(given_path):
        return not os.path.isdir(given_path) and os.access(given_path, os.W_OK)

    # File doesn't exist make dir path and file
    try:
        os.makedirs(os.path.dirname(given_path), exist_ok=True)
        open(given_path, 'a').close()
        # Check read permisson
        return os.access(given_path, os.W_OK)
    except OSError:
        return False

def get_password(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """If password is not set, get password from stdin"""
    if not constants.SETTINGS_PASSWORD in settings:
        password = ""
        while not password:
            password = getpass.getpass()

        settings[constants.SETTINGS_PASSWORD] = password
    return True

def check_password(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """Check if password is correct, and if not quit.

    In future also check for settings IGNORE_ERRORS, and continue if
    set."""
    if not frontend or not backend:
        return False
    try:
        ret = backend.process({constants.COMMAND: constants.COMMAND_STATS})
        values = ret[constants.RESPONSE_VALUES]
        if values[constants.RESPONSE_STATS_DECRYPTION_RATE] is not 1:
            return False
    except (KeyError, ValueError):
        return False
    return True

def main(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """Transport messages between frontend and backend.  Loop until
    frontend fails(if user types quit)"""
    while True:
        command = frontend.module.repl()
        ret = backend.module.process(command)
        front_ret = frontend.module.process(ret)[constants.RESPONSE]
        if front_ret is not constants.RESPONSE_OK:
            break
    return True

def clear_screen(settings: Dict[str, Any], frontend: Module, backend: Module) -> bool:
    """Send clear screen command to frontend"""
    frontend.process({constants.COMMAND: constants.COMMAND_QUIT,
                      constants.RESPONSE: constants.RESPONSE_OK}) # Hack for now
    return True
