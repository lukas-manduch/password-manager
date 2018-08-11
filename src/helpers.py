"""Module containing helper functions"""
import argparse
import getpass
import os
from typing import Any, Dict

import constants

# Disable unused argument warning
# pylint: disable=W0613

class Module:
    """Conevnience wrapper for modules (frontend and backend)"""
    def __init__(self, module: Any) -> None:
        self.module = module

    def message(self, content: str):
        """Send display request to module, return True if module returns ok"""
        pass

    def test(self):
        """Test"""
        pass

#### INIT FUNCTIONS ####
def create_password_file(settings: Dict[str, str], frontend: Module, backend: Module) -> bool:
    """If file and path defined in settings doesn't exist, create it"""
    if constants.SETTINGS_FILE_PATH not in settings:
        return False
    given_path = os.path.expanduser(settings[constants.SETTINGS_FILE_PATH])
    # Path cannot be dir already
    if os.path.exists(given_path):
        return not os.path.isdir(given_path)

    # File doesn't exist make dir path and file
    try:
        os.makedirs(os.path.dirname(given_path), exist_ok=True)
        open(given_path, 'a').close()
        # Check read permisson
        return os.access(given_path, os.R_OK)
    except OSError:
        return False

def parse_arguments(settings: Dict[str, str], frontend: Module, backend: Module) -> bool:
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

def set_settings(settings: Dict[str, str], frontend: Module, backend: Module) -> bool:
    """Merge default and parameter settings"""
    new_settings = constants.DEFAULT_SETTINGS
    new_settings.update(settings)
    settings.update(new_settings)
    return True

def get_password(settings: Dict[str, str], frontend: Module, backend: Module) -> bool:
    """If password is not set, get password from stdin"""
    if not constants.SETTINGS_PASSWORD in settings:
        password = ""
        while not password:
            password = getpass.getpass()

        settings[constants.SETTINGS_PASSWORD] = password
    return True

def check_password(settings: Dict[str, str], frontend: Module, backend: Module) -> bool:
    """Check if password is correct, and if not quit.  If settings has
    IGNORE_ERRORS set, continue anyway"""
    return True

def main(settings: Dict[str, str], frontend: Module, backend: Module) -> bool:
    """Do something"""
    return True
