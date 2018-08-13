"""Simple password manager - tool for storing encrypted notes.  Mainly
passwords :)
"""

from typing import Any, Dict

import helpers

INIT_LIST = [
    helpers.parse_arguments,
    helpers.set_settings,
    helpers.create_password_file,
    helpers.get_password,
    helpers.load_frontend,
    # Load backeng
    helpers.check_password,
    helpers.main,
]

if __name__ == "__main__":
    settings: Dict[str, Any] = {}
    FRONTEND = helpers.Module(None)
    BACKEND = helpers.Module(None)
    for func in INIT_LIST:
        print(str(func))
        if not func(settings, FRONTEND, BACKEND):
            print("Error")
            exit(1)
    print("Ok")
    print(settings)
    exit(0)
