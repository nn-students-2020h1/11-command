import unittest
import telegram
from unittest import mock
from unittest.mock import patch
import auxiliary_functions
import user_history
import os
from inline_handle import InlineKeyboardFactory, InlineCallback
from telegram import InlineKeyboardMarkup


class TestKeyboardFactory(unittest.TestCase):
    def test_contrast_keyboard(self):
        self.assertIsInstance(InlineKeyboardFactory.get_inline_contrast_keyboard(), InlineKeyboardMarkup)

    def test_coronavirus_keyboard(self):
        self.assertIsInstance(InlineKeyboardFactory.get_inline_coronavirus_keyboard(), InlineKeyboardMarkup)

    def test_news_keyboard(self):
        self.assertIsInstance(InlineKeyboardFactory.get_inline_news_keyboard(), InlineKeyboardMarkup)

    def test_stayhome_keyboard(self):
        self.assertIsInstance(InlineKeyboardFactory.get_inline_stayhome(), InlineKeyboardMarkup)

    def test_bloodtype_keyboard(self):
        self.assertIsInstance(InlineKeyboardFactory.get_inline_bloodtype(), InlineKeyboardMarkup)


class TestInlineCallback(unittest.TestCase):

    @patch("inline_handle.json.load", mock.MagicMock('{useless}'))
    @patch("inline_handle.json.dump", mock.MagicMock(return_value='{data}'))
    def test_add_data(self):
        mock_open_handler = mock.mock_open()
        with patch('telegram.Update') as mock_update:
            mock_update.message.chat.id = 2
        with patch('inline_handle.open', mock_open_handler, create=True):
            file_name, file_data = InlineCallback.update_data({"new": "data"}, "file.json")
        self.assertEqual(file_data, {"new": "data"})
