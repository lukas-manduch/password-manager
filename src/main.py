""" Simple password manager - tool for storing encrypted notes. mainly passwords :) """

import os
import sys

from core import PasswordFileManager
from settings import Settings


def get_password():
    return "abcd"

def get_file():
    return './tmp/testpass'


if __name__ == '__main__':
    settings = Settings(sys.argv)
    password = get_password()
    file_path = os.path.abspath(get_file())
    print("Using file: " + file_path)
