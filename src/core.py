"""Core - file with classes for core tasks in password manager, like
working with files, encryption, and searching
"""
import heapq
import re
import base64
import hashlib
from difflib import SequenceMatcher
from typing import List, Iterable, Tuple

import cryptography

import constants

# Disable TODO errors
#pylint: disable=W0511
# Disable Too few public methods warning
#pylint: disable=R0903

WHITESPACE_PATTERN = re.compile(r'\s')
PASSWORD_ENTRY_PATTERN = re.compile(r'(\d+)\s+(\d+)\s+(.*)', re.DOTALL)
KEY_SEARCH_JUNK_PATTERN = re.compile(r'\W+')


class PasswordFileManager:
    """Class for reading and writing binary data to file.  Takes list of
    entries and writes them in such a way, that they can be easily
    distinguished.

    PasswordFileManager is meant to be iterable.  Internal
    implementation will be probably changed in future, for better
    memory eficiency

    version - is counter updated on each change.  Other objects
    reading from this one should always check this number and if it is
    changed, act accordingly
    """

    # TODO: Checks for empty file, and file modified since read
    # TODO: Options for ignoring errors
    # TODO: Must be able to detect deleted separators


    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # Read contents to memory
        contents = self.read_contents()
        self.contents = parse_contents(contents)
        self.position = 0
        self.version = 0

    def __iter__(self):
        """Create iterator"""
        return self.PasswordFileManagerIterator(self.contents)

    def __getitem__(self, index) -> Tuple[str, str]:
        """Indexing operator"""
        return self.contents[index]

    def read_contents(self):
        """Load contents of file to memory"""
        contents = read_file(self.file_path).split(constants.SPLITTER)
        # Remove empty entries
        return filter(lambda x: True if x else False,
                      map(delete_whitespace, contents))

    def append_entry(self, first, second):
        """Append entry to list. For now, also write to file"""
        self.contents.append((first, second))
        self.save_contents()

    def save_contents(self):
        """Write current contents of this object to file"""
        write_file(self.file_path,
                   serialize_contents(self.contents))

    def delete_entry(self, index):
        """Remove entry from memory (shifts entries one index up)"""
        if index < len(self.contents):
            del self.contents[index]

    def delete_indices(self, indices: List[int]):
        """Delete all entries passed as indices via argument"""
        indices = sorted(indices, reverse=True)
        for index in indices:
            if index < len(self.contents):
                del self.contents[index]


    class PasswordFileManagerIterator:
        """Iterator for class PasswordFileManager"""
        def __init__(self, file_contents):
            """Parameter should be list of bytes"""
            self.contents = file_contents
            self.position = -1

        def __next__(self):
            self.position += 1
            if self.position < len(self.contents):
                return self.contents[self.position]
            raise StopIteration

###########################################################################

class KeyValueStore(object):
    """Wrapper around search function, which works with keys and
    values. Additionally provides hints to search, for ignoring non
    word characters.
    """

    # TODO: Check if data changed and therefore should be updated.

    KEY = 0
    VALUE = 1

    def __init__(self, entries: Iterable[Tuple[str, str]]) -> None:
        """Take reference to ENTRIES.  Expected format is iterable of
        key,value tuples.
        """
        self.entries = entries

    def find_key(self, key: str, max_results=10):
        """Search only on keys"""
        return search(self.entries, key, lambda x: x[self.KEY],
                      junk_filter=is_relevant_for_search, max_results=max_results)

    def find_fulltext(self, text: str, max_results=10):
        """Search on keys and also on values"""
        return search(self.entries, text, lambda x: x[self.KEY] + x[self.VALUE],
                      junk_filter=is_relevant_for_search, max_results=max_results)


###########################################################################


class Cipher(object):
    """Class for encryption decryption. In future cryptography library
    will probably be removed and replaced with direct calls to openssl"""

    def __init__(self, password: str) -> None:
        from cryptography.fernet import Fernet
        hashed = hashlib.sha256(str(password.encode).encode('utf-8'))
        key = base64.urlsafe_b64encode(hashed.digest())
        self.fernet = Fernet(key)

    def encrypt(self, secret: bytes) -> bytes:
        """Encrypt SECRET bytes with PASSWORD"""
        try:
            return self.fernet.encrypt(secret)
        except (cryptography.exceptions.InvalidSignature, cryptography.exceptions.InvalidKey):
            return b''

    def decrypt(self, cipher_text: bytes) -> bytes:
        """Decrypt CIPHER_TEXT bytes with PASSWORD"""
        try:
            return self.fernet.decrypt(cipher_text)
        except (cryptography.exceptions.InvalidSignature, cryptography.exceptions.InvalidKey):
            return b''

###########################################################################

###########################################
##############  METHODS  ##################
###########################################

def read_file(file_path: str) -> str:
    """Simple function for reading file"""
    with open(file_path, 'r') as opened_file:
        return opened_file.read()

def write_file(file_path: str, contents: str):
    """Write file contents to file"""
    # TODO: write even if disabled by user permissions
    with open(file_path, 'w') as opened_file:
        opened_file.write(contents)

def delete_whitespace(dirty_string: str) -> str:
    """Delete all spaces and newlines from DIRTY_STRING"""
    return re.sub(WHITESPACE_PATTERN, '', dirty_string)

def is_relevant_for_search(character: str) -> bool:
    """Function for hinting SequenceMatcher about junk letters"""
    if re.match(KEY_SEARCH_JUNK_PATTERN, character) is None:
        return False
    return True

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

def parse_entry(entry: bytes) -> Tuple[str, str]:
    """
    Given decrypted entry, return search key and secret value. If
    format is incorrect, or entry is corrupted, throws various exceptions
    """
    text = entry.decode('utf-8')
    match = re.fullmatch(PASSWORD_ENTRY_PATTERN, text)
    if not match:
        raise ValueError
    data = match.groups()
    text = process_entry(data[2])
    return (process_entry(text[0:int(data[0])]),
            process_entry(text[int(data[0]) + 1 :
                               int(data[0]) + 1 + int(data[1])]))

def parse_contents(contents) -> List[Tuple[str, str]]:
    """Given iterable object, containing entries from password file for
    each entry parse its contents (also decrypt) and return as list of
    tuples (key, value)

    Argument:
     Iterable object

    Return:
     List of tuples (key, value)

    """
    tmp = map(bytes.fromhex, contents)
    return list(map(parse_entry, tmp))

def serialize_contents(contents) -> str:
    """Given iterable of tuples (str, str), transform them to password
    manager format, eventually encrypt, than transform to hex and join
    to string
    """
    serialized = map(lambda x: serialize_entry(x[0], x[1]), contents)
    hserialized = map(lambda x: x.hex(), serialized)
    return constants.SPLITTER_NEWLINE.join(hserialized)


def _get_ratio(sequence_matcher, text):
    """Purpose of this function is to replace body of lambda, because
    search in Sequence_Matcher cannot be done in one command
    """
    sequence_matcher.set_seq1(text)
    return sequence_matcher.ratio()

def search(entries, text: str, func, junk_filter=None, max_results=10) -> List[int]:
    """Search in ENTRIES for TEXT. Return list of indices of entries with
    best match. Match max MAX_RESULTS entries. FUNC is given one entry
    and must transform it to one string.
    """
    matcher: SequenceMatcher = SequenceMatcher(junk_filter,
                                               autojunk=False)
    matcher.set_seq2(text)
    # Create list of (index, rating)
    indices = map(lambda x: (x[0], _get_ratio(matcher, func(x[1]))),
                  enumerate(entries))
    # Get only top MAX_RESULTS
    largest = heapq.nlargest(max_results, indices, key=lambda x: x[1])
    return list(map(lambda x: x[0], largest))
