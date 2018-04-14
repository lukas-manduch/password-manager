"""Tests for session module. Session is not covered by tests as much as other
modules, because it is basically joining all things together and therefore it
is harder to test."""

import unittest
import unittest.mock
from unittest.mock import patch
import session
import constants

# Disable missing docstring
# pylint: disable=C0111
class SessionControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.settings = {
            constants.SETTINGS_FILE_PATH : "abcd"
        }
        self.passwords_patcher = patch('session.PasswordFileManager')
        self.mock = self.passwords_patcher.start()
        self.mock.return_value = iter([
            ("key1", "value1"),
            ("key2", "value2")])

    def tearDown(self):
        self.passwords_patcher.stop()

    def test_update_status(self):
        session_controller = session.SessionController(self.settings)
        session_controller.update_status()
        self.assertEqual(True, session_controller.state)

    def test_update_status2(self):
        """Session controller cannot be in valid state without existing file"""
        session_controller = session.SessionController(self.settings)
        self.mock.side_effect = FileNotFoundError
        session_controller.update_status()
        self.assertEqual(False, session_controller.state)



if __name__ == '__main__':
    unittest.main()
