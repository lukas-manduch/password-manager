"""
Settings - Module for managing settings and initial phase of start
up (parsing arguments, printing error messages)
"""

DEFAULT_SETTINGS = {"file_path" : "./passwords.txt"}

def get_settings():
    "Return default settings"
    return DEFAULT_SETTINGS
