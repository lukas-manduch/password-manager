"""Tests for interaction commands and repl"""
import unittest
import unittest.mock

from interaction_commands import SearchInteractionCommand
from interaction_commands import AddInteractionCommand
import interaction
import constants

# pylint: disable=C0111
class EncoderDecoderTestCase(unittest.TestCase):
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


class InteractiveSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.command_list = [SearchInteractionCommand,
                             interaction.HelpInteractionCommand]

    def test_find_command(self):
        session = interaction.InteractiveSession(self.command_list)
        command = session.find_command('sea123')
        expect = {constants.COMMAND: constants.COMMAND_SEARCH,
                  constants.COMMAND_SEARCH_VALUE : '123'}
        self.assertEqual(expect, command.parse('123', {}))

        with self.assertRaises(interaction.InputNeeded):
            command = session.find_command('hel123')
            command.parse('hel123', {})

    def test_repl(self):
        expected = {'command': 'search', 'term': 'aa bb cc'}
        session = interaction.InteractiveSession(self.command_list)
        input_mock = unittest.mock.Mock(return_value="search aa bb cc")
        session.get_input = input_mock
        self.assertEqual(expected, session.repl())
        input_mock.assert_called_once_with()

    def test_keyboard_interrupt(self):
        """On first keyboard interrupt, command must be cancelled and on
        second exception thrown"""
        input_mock = unittest.mock.Mock(return_value="search aa bb cc")
        input_mock.side_effect = ['search', KeyboardInterrupt, KeyboardInterrupt]
        session = interaction.InteractiveSession(self.command_list)
        session.get_input = input_mock
        with self.assertRaises(KeyboardInterrupt):
            session.repl()
        self.assertEqual(3, input_mock.call_count)

if __name__ == '__main__':
    unittest.main()
