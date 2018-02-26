"""Simple password manager - tool for storing encrypted notes. mainly
passwords :)
"""

import sys

import interaction
import interaction_commands

COMMANDS_LIST = [interaction.HelpInteractionCommand,
                 interaction_commands.SearchInteractionCommand,
                 interaction_commands.DeleteInteractionCommand,
                 interaction_commands.ViewInteractionCommand]

def main():
    """Main function"""
    session = interaction.InteractiveSession(COMMANDS_LIST)
    print(session.repl())

if __name__ == '__main__':
    print("EHLO")
    if len(sys.argv) > 1:
        main()
    exit(0)
