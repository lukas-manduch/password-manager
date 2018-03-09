"""Tests for core functionality of password manager"""
import os
import tempfile
import unittest

import constants
import core


# pylint: disable=C0111
class EncoderDecoderTestCase(unittest.TestCase):
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

    def test_read_write(self):
        write = "Abcde fff"
        core.write_file(self.file_path, write)
        read = core.read_file(self.file_path)
        self.assertEqual(write, read)

    def tearDown(self):
        os.remove(self.file_path)


class KeyValueSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.tuples_list = [("key1", "my value"),
                            ("www.webpage.com", "my password"),
                            ("example.com", "Super stored text \nitem ssis securely"),
                            ("my reference", "Some secret note"),
                            ("My pin code", "721959297823996703"),
                            ("Some list", "- last stored item ...  securely entry")]
        constants.MAX_RESULTS = 2
        self.constants_tmp = constants.MAX_RESULTS

    def tearDown(self):
        constants.MAX_RESULTS = self.constants_tmp

    def test_searchable_store(self):
        expected = [('key1', 'my value'),
                    ('my reference', 'Some secret note')]
        store = core.SearchableDataStore(self.tuples_list)
        self.assertEqual(expected, store.search("my key", lambda x: x[0]))

    def test_searchable_store2(self):
        expected = [("example.com", "Super stored text \nitem ssis securely"),
                    ("Some list", "- last stored item ...  securely entry")]
        store = core.SearchableDataStore(self.tuples_list)
        self.assertEqual(expected, store.search("item securely", lambda x: x[1]))

    def test_find_fulltext(self):
        expected = [("Some list", "- last stored item ...  securely entry"),
                    ("example.com", "Super stored text \nitem ssis securely")]
        store = core.KeyValueStore(self.tuples_list)
        self.assertEqual(expected, store.find_fulltext("item securely"))

    def test_find_fulltext2(self):
        expected = [('key1', 'my value'),
                    ('my reference', 'Some secret note')]
        store = core.KeyValueStore(self.tuples_list)
        self.assertEqual(expected, store.find_fulltext("my key"))

    def test_find_key(self):
        expected = [('key1', 'my value'),
                    ('my reference', 'Some secret note')]
        store = core.KeyValueStore(self.tuples_list)
        self.assertEqual(expected, store.find_key("my key"))


if __name__ == '__main__':
    unittest.main()
