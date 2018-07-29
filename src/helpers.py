"""Module containing helper functions"""
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


def parse_settings(settings: Dict[str, str], frontend: Module, backend: Module) -> bool:
    """Do something"""
    pass
