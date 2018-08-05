"""Simple password manager - tool for storing encrypted notes.  Mainly
passwords :)
"""

from typing import Dict

import interaction
import helpers
import interaction_commands

COMMANDS_LIST = [
    interaction.HelpInteractionCommand,
    interaction_commands.SearchInteractionCommand,
    interaction_commands.AddInteractionCommand,
    interaction_commands.DeleteInteractionCommand,
    interaction_commands.ViewInteractionCommand,
]


INIT_LIST = [
    helpers.parse_arguments,
    helpers.set_settings,
    # Load frontend and backend
    helpers.create_password_file,
    helpers.get_password,
    helpers.main,
]

if __name__ == "__main__":
    settings: Dict[str, str] = {}
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
