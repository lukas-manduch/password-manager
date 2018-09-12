"""Module contains strings,definitions and default settings for password
manager"""

SPLITTER = "|"
SPLITTER_NEWLINE = "|\n"
MAX_RESULTS = 10
PROMPT_SYMBOL = "> "
PROGRAM_NAME = "passman"
###############


# Format passed to main session is like {COMMAND: COMMAND_ADD,
# COMMAND_ADD_KEY: key, COMMAND_ADD_VALUE:value}
COMMAND = "command"

SECRET_KEY = "key"
SECRET_VALUE = "value"
# Search
COMMAND_SEARCH = "search"
COMMAND_SEARCH_VALUE = "term"

# Add
COMMAND_ADD = "add"
COMMAND_ADD_KEY = SECRET_KEY
COMMAND_ADD_VALUE = SECRET_VALUE

# VIEW/SHOW
COMMAND_SHOW = "show"
COMMAND_SHOW_INDICES = "indices"

# Delete
COMMAND_DELETE = "delete"
COMMAND_DELETE_INDICES = "DELETE_INDICES"
COMMAND_DELETE_KEYWORD = "indices"
COMMAND_DELETE_KEYWORD_HELP = "Specify which indices from search should be deleted"

# Stats
COMMAND_STATS = "stats"

# Quit
COMMAND_QUIT = "quit"

# Response
RESPONSE = "status"
RESPONSE_ERROR = "error"
RESPONSE_OK = "ok"
RESPONSE_MISSING = "missing"

RESPONSE_VALUES = "values"

RESPONSE_ERROR_UNKNOWN_COMMAND = "Unknown command"
RESPONSE_ERROR_ARGUMENTS = "Bad or missing arguments"
RESPONSE_ERROR_OUT_OF_RANGE = "Given index is out of range"
RESPONSE_ERROR_REQUIRES_SEARCH = "Given command requires search before executing"
RESPONSE_ERROR_UNKNOWN_ERROR = "Unknown error occured, command was not successful"
RESPONSE_ERROR_INVALID_ARGUMENT = "Invalid argument passed to command"

# Values in dict returned by stats command
RESPONSE_STATS_DECRYPTION_RATE = "decryption_rate"  # <0,1>
RESPONSE_STATS_STATUS = "status"  # ok or error
##########################################

#################################################################################

# Settings
SETTINGS_FILE_PATH = "file_path"
SETTINGS_PASSWORD = "password"


SETTINGS_INTERACTION_COMMANDS_LIST = "interaction_commands"

DEFAULT_SETTINGS = {
    SETTINGS_FILE_PATH: "~/pass_man/passwords.txt",
    # List of classes for interactive session
    SETTINGS_INTERACTION_COMMANDS_LIST: [
        "HelpInteractionCommand",
        "AddInteractionCommand",
        "DeleteInteractionCommand",
        "SearchInteractionCommand",
        "ViewInteractionCommand",
        "QuitInteractionCommand",
    ],
}

##################################################################################

# Literals for interaction module
UNHANDLED_EXCEPTION = "Sorry, unhandled exception occured.\
\nWe will try to write current state to temporary file.\
\nIf you had anything important written, you\
\nshould replace your current version, with that."

SEARCH_INTERACTION_PROMPT = "Search"
SEARCH_INTERACTION_INFO = "Please enter search term"

ADD_INTERACTION_KEY_MISSING = "Please enter key which will represent this entry.\
                               \nThen enter value. Value must end with two empty lines"

ADD_INTERACTION_VALUE_MISSING = "Now enter value"

HELP_INTERACTION = """Here you can see list of available commands.  Command can be
represented by many synonyms and to call it you can usually type only
first few letters.  If you want to cancel command press Ctrl+C, second
time it closes whole application.  Commands usually have two versions,
fast form where you can specify everything on one line and complete
form where command interactively asks you for data (like "add key value"
for adding entry instead of just "add").  If command take indices as
parameters, you can usally specify more than one."""
HELP_AMBIGUOUS = "Sorry, command is ambiguous, try entering more characters:"
HELP_SEARCH_MANY = "Hint: To print other values, use show command"
HELP_SHOW_COMMAND = """[indices] After search, you can show full entry key and value.
Command takes as arguments indices returned by search"""
HELP_SEARCH_COMMAND = """[search term] Search in stored entries by key and return top
matches.  Indices next to shown entries are important for some other
commands like delete, which takes as argument theses indices"""
HELP_ADD_COMMAND = """[key] [value] Add new entry.  Entry is represented by key and
value.  Key should be one word representing whole entry (for example
url of webpage).  Value can be more than one line long.  After
entering value, enter two newlines in row which terminates command."""
HELP_DELETE_COMMAND = """[indices] Delete specified (by indices) entries."""
HELP_QUIT_COMMAND = """[indices] Clear screen and exit password manager (equal to
Ctrl-C)."""

### PARAMETERS ###

ARG_PASSOWRD = "--password"
ARG_PASSOWRD_SHORT = "-p"
ARG_PASSOWRD_DESCRIPTION = (
    "You can specify password as argument, and it won't be requested interactively"
)

ARG_FILEPATH = "--file"
ARG_FILEPATH_SHORT = "-f"
ARG_FILEPATH_DESCRIPTION = "Specify file which should be used for storing passwords,\
    instead of default ({})".format(
        DEFAULT_SETTINGS.get(SETTINGS_FILE_PATH, RESPONSE_MISSING))
