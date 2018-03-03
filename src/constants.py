"""Module contains strings and definitions for password manager"""
SPLITTER = '|'
MAX_RESULTS = 10
PROMPT_SYMBOL = '> '

# Main arguments
COMMAND = 'command'

# Search
COMMAND_SEARCH = 'search'
COMMAND_SEARCH_VALUE = 'term'
# Add
COMMAND_ADD = 'add'
COMMAND_ADD_KEY = 'key'
COMMAND_ADD_VALUE = 'value'



# Literals
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
