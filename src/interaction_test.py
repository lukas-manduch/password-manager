"""Tests for interaction commands and repl"""
import unittest
import unittest.mock

from interaction_commands import SearchInteractionCommand
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



if __name__ == '__main__':
    unittest.main()
