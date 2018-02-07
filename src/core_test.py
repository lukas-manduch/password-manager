import unittest
import core
import tempfile
import os

from core import PasswordFileManager


class EncoderDecoderTestCase(unittest.TestCase):
    def testEncode(self):
        self.assertEqual(11, 1 - (-10))

    def testDeleteWhitespace(self):
        self.assertEqual('ABCD', core.delete_whitespace('  A B \n CD '))
        self.assertEqual('', core.delete_whitespace('\r\t	 '))


class PasswordFileManagerTestCase(unittest.TestCase):
    def setUp(self):
        tup = tempfile.mkstemp(prefix='PasswordFileManagerTestCase')
        self.file_path = tup[1]
        os.write(tup[0],
                 b'4865 6 C 6c 6 F | 7369 72 | \
                 | | 686f772061726520796f753f ||| ')
        os.close(tup[0])

    def testIteration(self):
        results = list()
        expected_result = [b'Hello', b'sir', b'how are you?']
        for data in PasswordFileManager(self.file_path):
            results.append(data)
        self.assertEqual(expected_result ,results)

    def tearDown(self):
        os.remove(self.file_path)


if __name__ == '__main__':
    unittest.main()
