"""
Core - file with classes for core tasks in password manager, like
working with files, encryption, and searching
"""

import constants
import re


whitespace_pattern = re.compile(r'\s')
password_entry_pattern = re.compile(r'(\d+)\s+(\d+)\s+(.*)', re.DOTALL)


class PasswordFileManager:
    """
    Class for reading and writing binary data to file. Takes list of
    entries and writes them in such a way, that they can be easily
    distinguished.

    PasswordFileManager is meant to be iterable. Internal
    implementation will be probably changed in future, for better
    memory eficiency
    """
    def __init__(self, file_path: str, ignore_errors=False):
        self.file_path = file_path
        # Read contents to memory
        self.load_contents()
        self.position = 0

    def __iter__(self):
        return PasswordFileManagerIterator(self.contents)

    def load_contents(self) -> dict:
        """Load contents of file to memory"""
        contents = read_file(self.file_path).split(constants.SPLITTER)
        contents = filter(lambda x: True if len(x) else False ,
                          map(delete_whitespace, contents))
        self.contents = list(map(bytes.fromhex, contents))


class PasswordFileManagerIterator:
    def __init__(self, file_contents):
        """Parameter should be list of bytes"""
        self.contents = file_contents
        self.position = -1

    def __next__(self):
        self.position += 1
        if self.position < len(self.contents):
            return self.contents[self.position]
        raise StopIteration


def read_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def delete_whitespace(dirty_string: str) -> str:
    return re.sub(whitespace_pattern, '', dirty_string)


def process_entry(entry: str) -> str:
    """
    Operation applied on each string read or written to file.
    For now it only erases spaces
    """
    return entry.strip()


def serialize_entry(key, value) -> bytes:
    """
    Transform key and value to format:
    key_lenght value_lenght key_str value_str
    """
    key = process_entry(str(key))
    value = process_entry(str(value))
    return '{} {} {} {}'.format(len(key), len(value), key, value).encode('utf-8')


def parse_entry(entry: bytes) -> (str, str):
    """
    Given decrypted entry, return search key and secret value. If
    format is incorrect, or entry is corrupted, throws various exceptions
    """
    text = entry.decode('utf-8')
    data = re.fullmatch(password_entry_pattern, text ).groups()
    text = process_entry(data[2])
    return (process_entry(text[0:int(data[0])]),
            process_entry(text[int(data[0]) + 1 :
                               int(data[0]) + 1 + int(data[1])] ))
