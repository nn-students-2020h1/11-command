import unittest
from unittest import mock
from unittest.mock import patch, mock_open
import pymongo
import mongomock
import database
import telegram_commands
import time
import inline_handle


def simple_func():
    pass


def func_decor(func):
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner


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

    @patch("telegram_commands.json.load",
           mock.MagicMock({"location": "56.208975, 43.817691", "at_home": False, "blood": 2}))
    @patch("telegram_commands.json.dump", mock.MagicMock(return_value='{data}'))
    def test_calc_probability(self):
        with patch('webdriver_manager.chrome.ChromeDriverManager.install', side_effect=simple_func()):
            with patch('selenium.webdriver.Chrome', side_effect=simple_func()):
                with patch("builtins.open", mock_open(read_data="data")) as mock_file:
                    assert open("personal_0.json").read() == "data"
                    mock_file.assert_called_with("personal_0.json")
                    with patch("telegram_commands.BeautifulSoup", side_effect=simple_func()):
                        self.assertEqual(telegram_commands.calc_probability(0), format(0.500000001, '.8f'))

    '''@mongomock.patch(servers=(('testserver.com', 27017),))
    def test_command_get_stat_in_region(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            with patch('covid_stat.CovidRegionStat') as mock_covid:
                with patch('covid_stat.CovidRegionStat.get_list_of_regions', side_effect=simple_func()):
                    with patch('covid_stat.CovidRegionStat.get_and_save_csv_table', side_effect=simple_func()):
                        with patch('covid_stat.CovidRegionStat.get_plot_region', side_effect=simple_func()):
                            with patch('telegram_commands.bot.send_photo', side_effect=simple_func()):
                                self.update.message.text = "/stat Moscow"
                                mock_covid.return_value = None
                                mock_covid.get_list_of_regions.return_value = ["Moscow"]
                                mock_covid.get_specific_region_href.return_value = None
                                with patch("covid_stat.CovidRegionStat.get_list_of_regions", return_value=["Moscow"]):
                                    telegram_commands.command_get_stat_in_region(self.update, self.CallbackContext)'''
