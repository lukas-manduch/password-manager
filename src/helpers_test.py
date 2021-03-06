"""Tests for helpers.py"""

import os
import tempfile

import unittest
import unittest.mock
from unittest.mock import patch

import constants
import helpers


# Disable missing docstring warning
# pylint: disable=C0111

class CreateFileTestCase(unittest.TestCase):
    def test_create_password_file(self):
        mock = unittest.mock.MagicMock()
        filename = "some file.txt"
        with tempfile.TemporaryDirectory() as dir_name:
            settings = {constants.SETTINGS_FILE_PATH:
                        os.path.join(dir_name, filename)}
            self.assertTrue(helpers.create_password_file(settings, mock, mock))
            self.assertTrue(os.path.exists(os.path.join(dir_name, filename)))
            self.assertTrue(os.access(os.path.join(dir_name, filename), os.W_OK))

    def test_crete_directories(self):
        mock = unittest.mock.MagicMock()
        filename = "dir1/dir2/dir3/some file.txt"
        with tempfile.TemporaryDirectory() as dir_name:
            settings = {constants.SETTINGS_FILE_PATH:
                        os.path.join(dir_name, filename)}
            full_path = os.path.join(dir_name, filename)

            self.assertFalse(os.path.exists(full_path))
            self.assertTrue(helpers.create_password_file(settings, mock, mock))
            self.assertTrue(os.path.exists(full_path))
            self.assertTrue(os.access(full_path, os.W_OK))

    def test_crete_file_already_exists(self):
        """Create file must preserve content of already created file"""
        content = b'qpowieualsdkfh\x12'
        tmp_file = tempfile.NamedTemporaryFile('wb', delete=False)
        self.addCleanup(os.remove, tmp_file.name)
        settings = {constants.SETTINGS_FILE_PATH: tmp_file.name}
        mock = unittest.mock.MagicMock()

        tmp_file.write(content)
        tmp_file.close()
        self.assertTrue(helpers.create_password_file(settings, mock, mock))
        with open(tmp_file.name, 'rb') as tmpf:
            self.assertEqual(content, tmpf.read())

    @patch('helpers.os.access')
    def test_no_permission(self, mock):
        mock.return_value = True
        module_mock = unittest.mock.MagicMock()
        with tempfile.TemporaryFile() as new_file:
            settings = {constants.SETTINGS_FILE_PATH: new_file.name}
            ret1 = helpers.create_password_file(settings, module_mock, module_mock)
            mock.return_value = False
            ret2 = helpers.create_password_file(settings, module_mock, module_mock)
            self.assertEqual(ret1, True)
            self.assertEqual(ret2, False)
