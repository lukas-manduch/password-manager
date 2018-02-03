"""
Core - file with classes for core tasks in password manager, like
working with files, encryption, and searching
"""


class PasswordFileManager:
    """
    Class for reading and writing binary data to file. Takes list of
    entries and writes them in such a way, that they can be easily
    distinguished.
    """
    def __init__(self, file_path: str, ignore_errors=False):
        self.file_path = file_path
        # Read contents to memory

    def load_contents(self) -> dict:
        """Load contents of file to memory"""
        pass
