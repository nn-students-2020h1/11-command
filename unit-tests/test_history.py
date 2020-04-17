import unittest
import telegram
from unittest import mock
from unittest.mock import patch
import auxiliary_functions
import user_history
import os


class TestLoadHistory(unittest.TestCase):
    def test_no_user_history(self):
        with patch('telegram.Update') as mock_update:
            mock_update.message.chat.id = 0
        self.assertEqual(None, auxiliary_functions.load_history(mock_update))

    def test_load_empty_history(self):
        with patch('telegram.Update') as mock_update:
            mock_update.message.chat.id = 1
        self.assertEqual(None, auxiliary_functions.load_history(mock_update))


class TestWriteHistory(unittest.TestCase):
    def test_no_user_history(self):
        with patch('telegram.Update') as mock_update:
            mock_update.message.chat.id = 2
        with open("user_history/2.json", "r") as test_handle:
            self.assertEqual(test_handle.read(), '[]')
        os.remove("user_history/2.json")

    def test_correct_name(self):
        with patch('telegram.Update') as mock_update:
            os.chdir('..')
            mock_update.message.chat.id = 3
            print(os.getcwd())
            auxiliary_functions.save_history(mock_update)
            self.assertTrue(os.path.exists("user_history/3.json"))
            os.remove("user_history/3.json")
