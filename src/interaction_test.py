"""Tests for interaction commands and repl"""
# Disable missing docstring
# pylint: disable=C0111

import unittest
import unittest.mock

import constants
from interaction_commands import SearchInteractionCommand
from interaction_commands import AddInteractionCommand
from interaction_commands import ViewInteractionCommand
from interaction_commands import DeleteInteractionCommand
import interaction
import session


class TestInteractionCommand(interaction.InteractionCommand):
    """Test command for use by tests"""
    COMMANDS = ["test"]
    COMMAND_NAME = "test_command"

    def parse(self, user_input: str, additional_input: dict):
        raise NotImplementedError

# TESTS

class InteractionHelperMethodsTestCase(unittest.TestCase):
    def test_lognest_match(self):
        self.assertEqual(3, interaction.get_longest_match("search", "sea abc"))
        self.assertEqual(1, interaction.get_longest_match("search", "sabc"))
        self.assertEqual(6, interaction.get_longest_match("search", "search abc"))
        self.assertEqual(0, interaction.get_longest_match("search", "find abc"))

    def test_lognest_match2(self):
        self.assertEqual(6, interaction.get_longest_match("search", "Search abc"))
        self.assertEqual(3, interaction.get_longest_match("search", "SEAabc"))

    def test_get_best_match(self):
        res = interaction.get_best_match(
            "seaexample",
            ["find", "search", "simple"]
        )
        self.assertEqual((3, 'search'), res)

    def test_parse_numbers(self):
        func = interaction.parse_numbers
        self.assertEqual([], func(""))
        self.assertEqual([1, 2, 3], func("1[2]3"))
        self.assertEqual([1, 2, 3], func("1, 2, -3"))
        self.assertEqual([21, 22, 23], func("21.22,23"))
        self.assertEqual([], func("as;a,fa."))
        self.assertEqual([1], func("as;1,fa."))


class SearchCommandsTestCase(unittest.TestCase):
    def test_search_command_empty(self):
        parser = SearchInteractionCommand()
        with self.assertRaises(interaction.InputNeeded) as exc:
            parser.parse("   ", {})

        self.assertEqual(constants.SEARCH_INTERACTION_PROMPT, exc.exception.key_name)
        self.assertEqual(constants.SEARCH_INTERACTION_INFO, exc.exception.key_description)

    def test_search_command_normal(self):
        parser = SearchInteractionCommand()
        ret = parser.parse(" abcd efgh  ", {})
        self.assertEqual(constants.COMMAND_SEARCH, ret[constants.COMMAND])
        self.assertEqual(ret[constants.COMMAND_SEARCH_VALUE], "abcd efgh")

    def test_search_command_dict(self):
        parser = SearchInteractionCommand()
        ret = parser.parse("    ",
                           {constants.SEARCH_INTERACTION_PROMPT: "abcd"})
        self.assertEqual("abcd", ret[constants.COMMAND_SEARCH_VALUE])


class AddCommandsTestCase(unittest.TestCase):
    def test_value_to_list(self):
        inp = {constants.COMMAND_ADD_KEY : "abc",
               "1" : "line 1",
               "3" : "line 3",
               "2" : "line 2"}
        expected = ["line 1", "line 2", "line 3"]
        result = AddInteractionCommand.value_to_list(inp)
        self.assertEqual(expected, result)

    def test_parse_input_line(self):
        inp = "a-a.a/a s d f"
        result = AddInteractionCommand.parse_input_line(inp)
        self.assertEqual(('a-a.a/a', 's d f'), result)


    def test_expected_format(self):
        inp = {constants.COMMAND_ADD_KEY : "abc",
               "1" : "line 1",
               "5" : "",
               "3" : "line 3",
               "2" : "line 2",
               "4" : ""}
        out = AddInteractionCommand().parse("", inp)
        expected = {constants.COMMAND : constants.COMMAND_ADD,
                    constants.COMMAND_ADD_KEY : "abc",
                    constants.COMMAND_ADD_VALUE : "line 1\nline 2\nline 3\n\n"}
        self.assertEqual(expected, out)

    def test_load_oneline(self):
        line = " my_long-key.key some value  "
        out = AddInteractionCommand().parse(line, {})
        expected = {constants.COMMAND : constants.COMMAND_ADD,
                    constants.COMMAND_ADD_KEY : "my_long-key.key",
                    constants.COMMAND_ADD_VALUE : "some value"}
        self.assertEqual(expected, out)

    def test_get_value_or_raise(self):
        inp = []
        with self.assertRaises(interaction.InputNeeded) as _exc:
            out = AddInteractionCommand.get_value_or_raise(inp)
        inp.append("abc")
        with self.assertRaises(interaction.InputNeeded) as _exc:
            out = AddInteractionCommand.get_value_or_raise(inp)
        inp.append("")
        with self.assertRaises(interaction.InputNeeded) as _exc:
            out = AddInteractionCommand.get_value_or_raise(inp)
        inp.append("")
        out = AddInteractionCommand.get_value_or_raise(inp)
        self.assertEqual("abc\n\n", out)


class ShowCommandTestCase(unittest.TestCase):
    def test_command_wihtout_indices(self):
        command = ViewInteractionCommand()
        expected = {constants.COMMAND: constants.COMMAND_SHOW}
        self.assertEqual(expected, command.parse("", {}))
        self.assertEqual(expected, command.parse("qwe ere", {}))

    def test_command_wiht_indices(self):
        command = ViewInteractionCommand()
        expected = {constants.COMMAND: constants.COMMAND_SHOW,
                    constants.COMMAND_SHOW_INDICES: [1, 4, 5]}
        self.assertEqual(expected, command.parse("1 ,4, 5", {}))
        self.assertEqual(expected, command.parse("1 4 5", {}))
        self.assertEqual(expected, command.parse("1,4.5", {}))
        self.assertEqual(expected, command.parse("1 4a5", {}))


class DeleteCommandTestCase(unittest.TestCase):
    def setUp(self):
        self.command_list = [DeleteInteractionCommand,
                             interaction.HelpInteractionCommand]

    # Dont print to test output
    @unittest.mock.patch('interaction.print', unittest.mock.Mock())
    def test_command_wihtout_indices(self):
        interactive_session = interaction.InteractiveSession(self.command_list)
        input_mock = unittest.mock.Mock()
        input_mock.side_effect = ['delete', 'trash', '1 2']
        interactive_session.get_input = input_mock
        ret = interactive_session.repl()
        self.assertEqual(3, input_mock.call_count)
        self.assertEqual(ret[constants.COMMAND], constants.COMMAND_DELETE)
        self.assertEqual(ret[constants.COMMAND_DELETE_INDICES],
                         [1, 2])

    def test_command_with_indices(self):
        interactive_session = interaction.InteractiveSession(self.command_list)
        input_mock = unittest.mock.Mock()
        input_mock.side_effect = ['de1 , 3', '1 2']
        interactive_session.get_input = input_mock
        ret = interactive_session.repl()
        self.assertEqual(1, input_mock.call_count)
        self.assertEqual(ret[constants.COMMAND], constants.COMMAND_DELETE)
        self.assertEqual(ret[constants.COMMAND_DELETE_INDICES],
                         [1, 3])


class InteractiveSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.command_list = [SearchInteractionCommand,
                             interaction.HelpInteractionCommand,
                             TestInteractionCommand]

    def test_find_command(self):
        interactive_session = interaction.InteractiveSession(self.command_list)
        command = interactive_session.find_command('sea123')
        expect = {constants.COMMAND: constants.COMMAND_SEARCH,
                  constants.COMMAND_SEARCH_VALUE : '123'}
        self.assertEqual(expect, command.parse('123', {}))

        with self.assertRaises(interaction.InputNeeded):
            command = interactive_session.find_command('hel123')
            command.parse('hel123', {})

    def test_repl(self):
        expected = {'command': 'search', 'term': 'aa bb cc'}
        interactive_session = interaction.InteractiveSession(self.command_list)
        input_mock = unittest.mock.Mock(return_value="search aa bb cc")
        interactive_session.get_input = input_mock
        self.assertEqual(expected, interactive_session.repl())
        input_mock.assert_called_once_with()

    @unittest.mock.patch('interaction.InteractionCommand.call')
    def test_call_to_command(self, base_mock=None):
        """Test argument propagation to command object"""
        interactive = interaction.InteractiveSession(self.command_list)
        parameter = session.SessionController.ok_to_dict("test_command", ["aa"])
        interactive.process(parameter)
        self.assertEqual(base_mock.call_count, 1)


    @unittest.mock.patch(__name__ + '.TestInteractionCommand.call')
    def test_call_argument_list(self, call_mock):
        interactive = interaction.InteractiveSession(self.command_list)
        parameter = session.SessionController.ok_to_dict("test_command", ["ba", "ca"])
        interactive.process(parameter)

        args, kwargs = call_mock.call_args
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(args, ("ba", "ca"))
        self.assertEqual(kwargs, {})

    @unittest.mock.patch(__name__ + '.TestInteractionCommand.call')
    def test_call_argument_dict(self, call_mock):
        arguments = {"key1": "val1", "key2": []}
        interactive = interaction.InteractiveSession(self.command_list)
        parameter = session.SessionController.ok_to_dict("test_command", arguments)
        interactive.process(parameter)

        args, kwargs = call_mock.call_args
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(kwargs, arguments)
        self.assertEqual(args, ())

    @unittest.mock.patch(__name__ + '.TestInteractionCommand.call')
    def test_call_argument_int(self, call_mock):
        interactive = interaction.InteractiveSession(self.command_list)
        parameter = session.SessionController.ok_to_dict("test_command", 1)
        interactive.process(parameter)

        args, kwargs = call_mock.call_args
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(kwargs, {})
        self.assertEqual(args, (1,))

    # Dont print to test output
    @unittest.mock.patch('interaction.print', unittest.mock.Mock())
    def test_keyboard_interrupt(self):
        """On first keyboard interrupt, command must be cancelled and on
        second exception thrown"""
        input_mock = unittest.mock.Mock(return_value="search aa bb cc")
        input_mock.side_effect = ['search', KeyboardInterrupt, KeyboardInterrupt]
        interactive_session = interaction.InteractiveSession(self.command_list)
        interactive_session.get_input = input_mock
        with self.assertRaises(KeyboardInterrupt):
            interactive_session.repl()
        self.assertEqual(3, input_mock.call_count)


if __name__ == '__main__':
    unittest.main()
