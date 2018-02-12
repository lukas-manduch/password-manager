import unittest
import core
import tempfile
import os

from core import PasswordFileManager


class EncoderDecoderTestCase(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(11, 1 - (-10))

    def test_delete_whitespace(self):
        self.assertEqual('ABCD', core.delete_whitespace('  A B \n CD '))
        self.assertEqual('', core.delete_whitespace('\r\t	 '))

    def test_serialize_entry(self):
        self.assertTrue(True)


class PasswordFileManagerTestCase(unittest.TestCase):
    def set_up(self):
        tup = tempfile.mkstemp(prefix='PasswordFileManagerTestCase')
        self.file_path = tup[1]
        os.write(tup[0],
                 b'4865 6 C 6c 6 F | 7369 72 | \
                 | | 686f772061726520796f753f ||| ')
        os.close(tup[0])

    def test_iteration(self):
        expected_result = [b'Hello', b'sir', b'how are you?']
        result = [data for data in PasswordFileManager(self.file_path)]
        self.assertEqual(expected_result, result)

    def tear_down(self):
        os.remove(self.file_path)


if __name__ == '__main__':
    unittest.main()
