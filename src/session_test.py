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
            constants.SETTINGS_FILE_PATH : "abcd",
            constants.SETTINGS_PASSWORD : "bfeg",
        }
        self.file_content = [("key1", "value1"),
                             ("key2", "value2"),
                             ("key3", "val3")]
        self.mock = unittest.mock.MagicMock()
        self.mock.__iter__.return_value = iter(self.file_content)
        self.mock.__getitem__ = lambda s, x: self.file_content[x]
        self.passwords_patcher = patch('session.PasswordFileManager',
                                       return_value=self.mock)
        self.import_mock = self.passwords_patcher.start()
        self.addCleanup(self.import_mock.stop)

    def test_invalid_command(self):
        session_controller = session.SessionController(self.settings)
        ret = session_controller.process({constants.COMMAND:
                                          "abcd"})
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)
        self.assertEqual(ret[constants.RESPONSE_ERROR],
                         constants.RESPONSE_ERROR_UNKNOWN_COMMAND)
        # No command at all
        ret = session_controller.process({"asda": "abcd"})
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)
        self.assertEqual(ret[constants.RESPONSE_ERROR],
                         constants.RESPONSE_ERROR_UNKNOWN_COMMAND)

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
        self.assertEqual(self.mock.save_contents.call_count, 1)

    def test_add_failure(self):
        session_controller = session.SessionController(self.settings)
        self.mock.append_entry.side_effect = OSError
        session_controller.update_status()
        ret = session_controller.add("my key", "my_value")
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)

    def test_search(self):
        session_controller = session.SessionController(self.settings)
        session_controller.update_status()
        ret = session_controller.search("2")
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_OK)
        self.assertEqual(len(ret[constants.RESPONSE_VALUES]), 3)

    def test_search_many_entries(self):
        """Test for bug"""
        file_contents = [("key1", "value1")] * 100000
        file_contents.append(("key2", "value2"))
        mock = unittest.mock.MagicMock()
        mock.__iter__.return_value = list(iter(file_contents))
        mock.__getitem__ = lambda s, x: file_contents[x]

        with patch('session.PasswordFileManager', return_value=mock):

            session_controller = session.SessionController(self.settings)
            ret = session_controller.process(
                {constants.COMMAND: constants.COMMAND_SEARCH,
                 constants.COMMAND_SEARCH_VALUE: "2"}
            )

            self.assertEqual(constants.RESPONSE_OK, ret[constants.RESPONSE])
            self.assertEqual(
                "key2", ret[constants.RESPONSE_VALUES][0][constants.SECRET_KEY]
            )

    def test_show_before_search(self):
        session_controller = session.SessionController(self.settings)
        my_mock = unittest.mock.Mock(wraps=session_controller.show)
        param = {constants.COMMAND: constants.COMMAND_SHOW}

        with patch('session.SessionController.show', new=my_mock):
            ret = session_controller.process(param)
            self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)
            # Change param value
            param[constants.COMMAND_SHOW_INDICES] = [1, 2]
            ret = session_controller.process(param)
            self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)
            self.assertEqual(my_mock.call_count, 2)

    def test_show_after_search(self):
        session_controller = session.SessionController(self.settings)
        my_mock = unittest.mock.Mock(wraps=session_controller.show)
        param = {constants.COMMAND: constants.COMMAND_SHOW}
        session_controller.process({constants.COMMAND: constants.COMMAND_SEARCH,
                                    constants.COMMAND_SEARCH_VALUE: "key1"})
        with patch('session.SessionController.show', new=my_mock):
            # Indices not specified
            ret = session_controller.process(param)
            self.assertEqual(len(ret[constants.RESPONSE_VALUES]), 3)
            # Specify index
            param[constants.COMMAND_SHOW_INDICES] = [1]
            ret = session_controller.process(param)
            self.assertEqual(len(ret[constants.RESPONSE_VALUES]), 1)
            self.assertEqual(ret[constants.RESPONSE_VALUES][0]['key'], 'key2')

    def test_show_invalid_index(self):
        session_controller = session.SessionController(self.settings)
        assert len(self.file_content) == 3
        session_controller.process({constants.COMMAND: constants.COMMAND_SEARCH,
                                    constants.COMMAND_SEARCH_VALUE: "key1"})
        # Indices off by one
        param = {constants.COMMAND: constants.COMMAND_SHOW,
                 constants.COMMAND_SHOW_INDICES: [2, 3]}
        ret = session_controller.process(param)
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)
        # Correct indices
        param = {constants.COMMAND: constants.COMMAND_SHOW,
                 constants.COMMAND_SHOW_INDICES: [1, 2]}
        ret = session_controller.process(param)
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_OK)

    def test_delete_withou_search(self):
        session_cont = session.SessionController(self.settings)
        ret = session_cont.process({constants.COMMAND: constants.COMMAND_DELETE,
                                    constants.COMMAND_DELETE_INDICES: []})
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)
        self.assertEqual(ret[constants.RESPONSE_ERROR], constants.RESPONSE_ERROR_REQUIRES_SEARCH)

    def test_delete_invalid_argument(self):
        session_cont = session.SessionController(self.settings)
        ret = session_cont.process({constants.COMMAND: constants.COMMAND_DELETE,
                                    constants.COMMAND_DELETE_INDICES: 3})
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)
        self.assertEqual(ret[constants.RESPONSE_ERROR], constants.RESPONSE_ERROR_INVALID_ARGUMENT)

    @patch("session.KeyValueStore.find_key")
    def test_delete_array(self, key_value_mock):
        session_cont = session.SessionController(self.settings)
        key_value_mock.return_value = [0, 1, 2]
        # Search
        session_cont.update_status()
        session_cont.search("aa")
        # Delete
        ret = session_cont.process({constants.COMMAND: constants.COMMAND_DELETE,
                                    constants.COMMAND_DELETE_INDICES: [1, 2]})
        self.assertEqual(self.mock.delete_indices.call_count, 1)
        self.assertEqual(self.mock.save_contents.call_count, 1)
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_OK)
        self.mock.delete_indices.assert_called_with([1, 2])
        # Search again
        session_cont.update_status()
        session_cont.search("aa")
        # Delete
        ret = session_cont.process({constants.COMMAND: constants.COMMAND_DELETE,
                                    constants.COMMAND_DELETE_INDICES: [1, 2, 3]})
        # Won't be called again
        self.assertEqual(self.mock.delete_indices.call_count, 1)
        self.assertEqual(self.mock.save_contents.call_count, 1)
        self.assertEqual(ret[constants.RESPONSE], constants.RESPONSE_ERROR)
        self.assertEqual(ret[constants.RESPONSE_ERROR],
                         constants.RESPONSE_ERROR_OUT_OF_RANGE)

    def test_stats_valid(self):
        rate = 0.72
        self.mock.success = rate
        session_cont = session.SessionController(self.settings)
        expected = session.SessionController.ok_to_dict(
            constants.COMMAND_STATS,
            {
                constants.RESPONSE_STATS_STATUS: constants.RESPONSE_OK,
                constants.RESPONSE_STATS_DECRYPTION_RATE: rate

            }
        )
        arg = {constants.COMMAND: constants.COMMAND_STATS}

        ret = session_cont.process(arg)
        self.assertEqual(expected, ret)

    def test_ok_to_dict(self):
        command_name = "abcd"
        ret = session.SessionController.ok_to_dict(command_name)
        expected = {constants.RESPONSE: constants.RESPONSE_OK,
                    constants.COMMAND: command_name}
        self.assertEqual(ret, expected)
        value = [1, 2, 2]
        ret = session.SessionController.ok_to_dict(command_name, value)
        expected = {constants.RESPONSE: constants.RESPONSE_OK,
                    constants.COMMAND: command_name,
                    constants.RESPONSE_VALUES: value}

if __name__ == '__main__':
    unittest.main()
