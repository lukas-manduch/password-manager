import unittest

import interaction

class EncoderDecoderTestCase(unittest.TestCase):
    def test_lognest_match(self):
        self.assertEqual(3, interaction._get_longest_match("search", "sea abc"))
        self.assertEqual(1, interaction._get_longest_match("search", "sabc"))
        self.assertEqual(6, interaction._get_longest_match("search", "search abc"))
        self.assertEqual(0, interaction._get_longest_match("search", "find abc"))

    def test_lognest_match2(self):
        self.assertEqual(6, interaction._get_longest_match("search", "Search abc"))
        self.assertEqual(3, interaction._get_longest_match("search", "SEAabc"))





if __name__ == '__main__':
    unittest.main()
