"""Simple password manager - tool for storing encrypted notes.  Mainly
passwords :)
"""



import interaction
import interaction_commands
import settings
from session import SessionController

COMMANDS_LIST = [interaction.HelpInteractionCommand,
                 interaction_commands.SearchInteractionCommand,
                 interaction_commands.AddInteractionCommand,
                 interaction_commands.DeleteInteractionCommand,
                 interaction_commands.ViewInteractionCommand]

def main():
    """Main function"""
    cont = SessionController(settings.get_settings())

    session = interaction.InteractiveSession(COMMANDS_LIST)
    while True:
        result = session.repl()
        print(result)

        print(cont.process(result))



if __name__ == '__main__':
    SessionController(settings.get_settings())
    print("EHLO")
    main()
    exit(0)
