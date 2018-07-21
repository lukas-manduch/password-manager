"""Tests for core functionality of password manager"""
from functools import partial
import os
import tempfile
import unittest
import unittest.mock
from unittest.mock import patch

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

    def test_parse_contents(self):
        expect = [('l', 'aa'), ('Hello', 'yeti')]
        values = [b'1 2 l aa', b'5 4 Hello yeti']
        en_cipher = core.Cipher("some long password")
        hvalues = [en_cipher.encrypt(val).hex() for val in values]
        de_cipher = core.Cipher("some long password")
        self.assertEqual(expect, core.parse_contents(hvalues, de_cipher))

    @unittest.skip("Serialize contents must be tested differently")
    def test_serialize_contents(self):
        pass
        #expect = "312032206c206161|\n3520342048656c6c6f2079657469"
        #inp = [('l', 'aa'), ('Hello', 'yeti')]
        #self.assertEqual(expect, core.serialize_contents(inp))



class PasswordFileManagerIOTestCase(unittest.TestCase):
    def test_iteration(self):
        file_content = [('my key', 'my\nvalue'),
                        ('some_other_key', 'some weird\nvalue')]
        tup = tempfile.mkstemp(prefix='PasswordFileManagerIOTestCase')
        os.close(tup[0])
        file_path = tup[1]
        self.addCleanup(os.remove, file_path)

        pass_file = core.PasswordFileManager(file_path, "abcd123")
        for entry in file_content:
            pass_file.append_entry(entry[0], entry[1])
        pass_file.save_contents()

        pass_file2 = core.PasswordFileManager(file_path, "abcd123")
        result = [data for data in pass_file2]

        self.assertEqual(file_content, result)
        self.assertEqual(1, pass_file2.success)

    def test_read_write(self):
        tup = tempfile.mkstemp(prefix='PasswordFileManagerIOTestCase')
        os.close(tup[0])
        self.addCleanup(os.remove, tup[1])

        write = "Abcde fff"
        core.write_file(tup[1], write)
        read = core.read_file(tup[1])
        self.assertEqual(write, read)


class PasswordFileManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.content = [("key 1", "some val"),
                        ("key 2", "other val"),
                        ("key1 3", "value"),
                        ("key 4", "val"),
                        ("key 6", "1234")]
        self.mock1 = patch("core.PasswordFileManager.read_contents")
        self.mock1.start()
        self.mock2 = patch("core.parse_contents", return_value=self.content[:])
        self.mock2.start()
        self.addCleanup(self.mock1.stop)
        self.addCleanup(self.mock2.stop)

    def test_delete_one_entry(self):
        pass_man = core.PasswordFileManager("", "")
        pass_man.delete_entry(1)
        expected = self.content[:]
        del expected[1]
        self.assertEqual(expected, pass_man.contents)

    def test_delete_multiple_entries(self):
        pass_man = core.PasswordFileManager("", "")
        pass_man.delete_indices([4, 4, 4, 0, 1])
        expected = self.content[:]
        del expected[4]
        del expected[1]
        del expected[0]
        self.assertEqual(expected, pass_man.contents)


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
        expected = [0, 3]
        func = partial(core.search, self.tuples_list, max_results=2)
        self.assertEqual(expected, func("my key", lambda x: x[0]))

    def test_searchable_store2(self):
        expected = [2, 5]
        func = partial(core.search, self.tuples_list, max_results=2)
        self.assertEqual(expected, func("item securely", lambda x: x[1]))

    def test_find_fulltext(self):
        expected = [5, 2]
        store = core.KeyValueStore(self.tuples_list)
        self.assertEqual(expected, store.find_fulltext("item securely", max_results=2))

    def test_find_fulltext2(self):
        expected = [0, 3]
        store = core.KeyValueStore(self.tuples_list)
        self.assertEqual(expected, store.find_fulltext("my key", max_results=2))

    def test_find_key(self):
        expected = [0, 3]
        store = core.KeyValueStore(self.tuples_list)
        self.assertEqual(expected, store.find_key("my key", max_results=2))


class EncryptionDecryptionTestCase(unittest.TestCase):
    def test_simple_encryption(self):
        cipher1 = core.Cipher('pass')
        cipher2 = core.Cipher('pass')
        plaintext = b'Hello, how are you? This is pretty \n long literal'
        encrypted = cipher1.encrypt(plaintext)
        self.assertNotEqual(plaintext, encrypted)
        decrypted = cipher2.decrypt(encrypted)
        self.assertEqual(plaintext, decrypted)


if __name__ == '__main__':
    unittest.main()
