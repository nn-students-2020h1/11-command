import unittest
from unittest import mock
from unittest.mock import patch
import pymongo
import mongomock
import database
import telegram_commands
import time
import inline_handle


class TestFunctions(unittest.TestCase):
    @mongomock.patch(servers=(('testserver.com', 27017),))
    def setUp(self) -> None:
        self.time = time.localtime()
        self.update = mock.MagicMock()
        self.context = mock.MagicMock()
        self.CallbackContext = mock.MagicMock()
        self.update.message.from_user.id = 0
        self.update.effective_user.first_name = 'Test Name'
        self.update.message.text = 'Test text test text'
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.UserDataBase()

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def tearDown(self) -> None:
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.UserDataBase()

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_start(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            self.assertEqual(telegram_commands.command_start(self.update, self.CallbackContext), "Test Name")

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_help(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            self.assertEqual(telegram_commands.command_chat_help(self.update, self.CallbackContext), "success")

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_echo(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            self.update.message.text = "Who created you?"
            self.assertEqual(telegram_commands.command_echo(self.update, self.CallbackContext), "11 team")

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_command_history(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            with patch('auxiliary_functions.time') as mock_time:
                mock_time.strftime.return_value = "00:00:00"
                self.update.message.text = "Who created you?"
                telegram_commands.command_echo(self.update, self.CallbackContext)
                self.assertEqual(telegram_commands.command_history(self.update, self.CallbackContext),
                                 "<b>function:</b> command_echo, <b>text</b>: Who created you?, <b>time</b>: 00:00:00\n")

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_command_get_news(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            with patch('telegram_commands.bot') as mock_bot:
                mock_bot.send_message.return_value = None
                self.assertEqual(telegram_commands.command_get_news(self.update, self.CallbackContext),
                                 inline_handle.InlineKeyboardFactory.get_inline_news_keyboard())

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_command_recommendation(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            self.assertIsInstance(telegram_commands.command_recommendation(self.update, self.CallbackContext), str)
