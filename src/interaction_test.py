import unittest

import interaction
import constants


class EncoderDecoderTestCase(unittest.TestCase):
    def test_lognest_match(self):
        self.assertEqual(3, interaction.get_longest_match("search", "sea abc"))
        self.assertEqual(1, interaction.get_longest_match("search", "sabc"))
        self.assertEqual(6, interaction.get_longest_match("search", "search abc"))
        self.assertEqual(0, interaction.get_longest_match("search", "find abc"))

    def test_lognest_match2(self):
        self.assertEqual(6, interaction.get_longest_match("search", "Search abc"))
        self.assertEqual(3, interaction.get_longest_match("search", "SEAabc"))


class InteractionCommandsTestCase(unittest.TestCase):
    def test_search_command_empty(self):
        parser = interaction.SearchInteractionCommand()
        with self.assertRaises(interaction.InputNeeded) as exc:
            parser.parse("sea   ", {})

        self.assertEqual(constants.SEARCH_INTERACTION_PROMPT, exc.exception.key_name)
        self.assertEqual(constants.SEARCH_INTERACTION_INFO, exc.exception.key_description)

    def test_search_command_normal(self):
        parser = interaction.SearchInteractionCommand()
        ret = parser.parse("search  abcd efgh  ", {})
        self.assertEqual(constants.COMMAND_SEARCH, ret[constants.COMMAND])
        self.assertEqual(ret[constants.COMMAND_SEARCH_VALUE], "abcd efgh")

    def test_search_command_dict(self):
        parser = interaction.SearchInteractionCommand()
        ret = parser.parse("    ",
                           {constants.SEARCH_INTERACTION_PROMPT: "abcd"})
        self.assertEqual("abcd", ret[constants.COMMAND_SEARCH_VALUE])


class InteractiveSessionTestCase(unittest.TestCase):
    def test_get_best_match(self):
        res = interaction.get_best_match(
            "seaexample",
            ["find", "search", "simple"]
        )
        self.assertEqual((3, 'search'), res)


if __name__ == '__main__':
    unittest.main()
