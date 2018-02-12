import unittest
import core
import tempfile
import os

class EncoderDecoderTestCase(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(11, 1 - (-10))

    def test_delete_whitespace(self):
        self.assertEqual('ABCD', core.delete_whitespace('  A B \n CD '))
        self.assertEqual('', core.delete_whitespace('\r\t	 '))

    def test_serialize_entry(self):
        self.assertEqual(b'6 7 my key val val',
                         core.serialize_entry('my key', 'val val'))

    def test_parse_entry(self):
        self.assertEqual(('my key', 'some\nvalue'),
                         core.parse_entry(b'6 10 my key some\nvalue'))




class PasswordFileManagerTestCase(unittest.TestCase):
    def setUp(self):
        tup = tempfile.mkstemp(prefix='PasswordFileManagerTestCase')
        self.file_path = tup[1]
        os.write(tup[0],
                 b'4865 6 C 6c 6 F | 7369 72 | \
                 | | 686f772061726520796f753f ||| ')
        os.close(tup[0])

    def test_iteration(self):
        expected_result = [b'Hello', b'sir', b'how are you?']
        result = [data for data in core.PasswordFileManager(self.file_path)]
        self.assertEqual(expected_result, result)

    def tearDown(self):
        os.remove(self.file_path)


if __name__ == '__main__':
    unittest.main()
