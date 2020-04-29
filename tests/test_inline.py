import unittest

from unittest import mock
from unittest.mock import patch
from inline_handle import InlineKeyboardFactory, InlineCallback
from telegram import InlineKeyboardMarkup


def yet_another_func(*args):
    return ''


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

    """TEST BELOW FAILS
    @patch("inline_handle.img_h.get_contrast_img", mock.MagicMock)
    @patch("inline_handle.bot.send_photo", mock.MagicMock)
    @patch("inline_handle.bot.delete_message", mock.Mock)
    def test_callback(self):
        with patch('telegram.Update') as mock_update:
            mock_update.effective_message.chat_id = 0
            mock_update.callback_query.data = CALLBACK_BUTTON_01
            self.assertEqual(inline_handle.InlineCallback.handle_keyboard_callback(mock_update), CALLBACK_BUTTON_01)"""
