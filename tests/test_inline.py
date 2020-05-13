import unittest
import inline_handle

from unittest import mock
from unittest.mock import patch
from inline_handle import InlineKeyboardFactory, InlineCallback
from telegram import InlineKeyboardMarkup


def simple_func(factor=None, base_img=None, res_img=None, chat_id=None):
    pass


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

    def test_uno_choose_player_keyboard(self):
        self.assertIsInstance(InlineKeyboardFactory.get_inline_uno_choose_player(), InlineKeyboardMarkup)

    def test_inline_uno_choose_color(self):
        self.assertIsInstance(InlineKeyboardFactory.get_inline_uno_choose_color(), InlineKeyboardMarkup)


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

    def test_callback_01(self):
        with patch('telegram.Update') as mock_update:
            mock_update.effective_message.chat_id = 0
            mock_update.callback_query.data = inline_handle.CALLBACK_BUTTON_01
            with patch('inline_handle.InlineCallback.change_contrast_level') as mock_func:
                mock_func.return_value = None
                self.assertEqual(inline_handle.InlineCallback.handle_keyboard_callback(mock_update),
                                 inline_handle.CALLBACK_BUTTON_01)

    def test_callback_05(self):
        with patch('telegram.Update') as mock_update:
            mock_update.effective_message.chat_id = 0
            mock_update.callback_query.data = inline_handle.CALLBACK_BUTTON_05
            with patch('inline_handle.InlineCallback.change_contrast_level') as mock_func:
                mock_func.return_value = None
                self.assertEqual(inline_handle.InlineCallback.handle_keyboard_callback(mock_update),
                                 inline_handle.CALLBACK_BUTTON_05)

    def test_callback_m01(self):
        with patch('telegram.Update') as mock_update:
            mock_update.effective_message.chat_id = 0
            mock_update.callback_query.data = inline_handle.CALLBACK_BUTTON_m01
            with patch('inline_handle.InlineCallback.change_contrast_level') as mock_func:
                mock_func.return_value = None
                self.assertEqual(inline_handle.InlineCallback.handle_keyboard_callback(mock_update),
                                 inline_handle.CALLBACK_BUTTON_m01)

    def test_callback_m05(self):
        with patch('telegram.Update') as mock_update:
            mock_update.effective_message.chat_id = 0
            mock_update.callback_query.data = inline_handle.CALLBACK_BUTTON_m05
            with patch('inline_handle.InlineCallback.change_contrast_level') as mock_func:
                mock_func.return_value = None
                self.assertEqual(inline_handle.InlineCallback.handle_keyboard_callback(mock_update),
                                 inline_handle.CALLBACK_BUTTON_m05)
