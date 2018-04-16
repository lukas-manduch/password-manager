"""Tests for session module. Session is not covered by tests as much as other
modules, because it is basically joining all things together and therefore it
is harder to test."""

import unittest
import unittest.mock
from unittest.mock import patch

import constants
import session

# Disable missing docstring warning
# pylint: disable=C0111
class SessionControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.settings = {
            constants.SETTINGS_FILE_PATH : "abcd"
        }
        self.mock = unittest.mock.MagicMock()
        self.mock.__iter__.return_value = iter([("key1", "value1"),
                                                ("key2", "value2")])
        self.mock.aa.return_value = 1
        self.passwords_patcher = patch('session.PasswordFileManager',
                                       return_value=self.mock)
        self.import_mock = self.passwords_patcher.start()
        self.addCleanup(self.passwords_patcher.stop)

    def test_update_status(self):
        session_controller = session.SessionController(self.settings)
        session_controller.update_status()
        self.assertEqual(True, session_controller.state)

    def test_update_status2(self):
        """Session controller cannot be in valid state without existing file"""
        session_controller = session.SessionController(self.settings)
        self.import_mock.side_effect = FileNotFoundError
        session_controller.update_status()
        self.assertEqual(False, session_controller.state)

    def test_error_to_dict(self):
        ret = session.SessionController.error_to_dict("abc")
        self.assertEqual(ret[constants.RESPONSE_ERROR], "abc")
        self.assertEqual(constants.RESPONSE_ERROR, ret[constants.RESPONSE])

    def test_process_empty(self):
        session_controller = session.SessionController(self.settings)
        ret = session_controller.process({})
        self.assertEqual(constants.RESPONSE_ERROR, ret[constants.RESPONSE])

    def test_add_success(self):
        session_controller = session.SessionController(self.settings)
        session_controller.update_status()
        ret = session_controller.add("my key", "my_value")
        self.mock.append_entry.assert_called_once_with("my key", "my_value")
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_OK)

    def test_add_failure(self):
        session_controller = session.SessionController(self.settings)
        self.mock.append_entry.side_effect = OSError
        session_controller.update_status()
        ret = session_controller.add("my key", "my_value")
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)


if __name__ == '__main__':
    unittest.main()
