"""Module contains strings and definitions for password manager"""
SPLITTER = '|'
SPLITTER_NEWLINE = '|\n'
MAX_RESULTS = 10
PROMPT_SYMBOL = '> '

# Main arguments

# Format passed to main session is like {COMMAND: COMMAND_ADD,
# COMMAND_ADD_KEY: key, COMMAND_ADD_VALUE:value}
COMMAND = 'command'

# Search
COMMAND_SEARCH = 'search'
COMMAND_SEARCH_VALUE = 'term'

# Add
COMMAND_ADD = 'add'
COMMAND_ADD_KEY = 'key'
COMMAND_ADD_VALUE = 'value'

# Response
RESPONSE = 'status'
RESPONSE_ERROR = 'error'
RESPONSE_OK = 'ok'

RESPONSE_ERROR_UNKNOWN_COMMAND = "Unknown command"
RESPONSE_ERROR_ARGUMENTS = "Bad or missing arguments"

# Settings
SETTINGS_FILE_PATH = "file_path"

# Literals for interaction module
UNHANDLED_EXCEPTION = "Sorry, unhandled exception occured.\
\nWe will try to write current state to temporary file.\
\nIf you had anything important written, you\
\nshould replace your current version, with that."

SEARCH_INTERACTION_PROMPT = "Search"
SEARCH_INTERACTION_INFO = "Please enter search term"

ADD_INTERACTION_KEY_MISSING = "Command - Add\
\nPlease enter key which will represent this entry.\
\nThen enter value. Value must end with two empty lines"

HELP_AMBIGUOUS = "Sorry command is ambiguous:\n"
