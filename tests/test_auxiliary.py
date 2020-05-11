import unittest
import mongomock
import auxiliary_functions
import pymongo
import database
import time
from unittest.mock import patch
from auxiliary_functions import handle_command, handle_image
from tests.test_history import get_action, get_dataframe


@handle_command
def simple_task(update):
    return update


@handle_image
def simple_image(update):
    return update


def simple_action(chat_id=None, action=None, photo=None, mode=None):
    return None


class TestCommandHandle(unittest.TestCase):

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def setUp(self) -> None:
        self.update = unittest.mock.MagicMock()
        self.time = time.localtime()
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.UserDataBase()

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_simple_command(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            self.update.effective_user.first_name = "Test Name"
            self.update.message.text = "test text"
            self.update.message.chat_id = 0
            with patch('auxiliary_functions.time.localtime') as mock_time:
                mock_time.return_value = self.time
                simple_task(self.update)
            self.assertEqual(auxiliary_functions.db_user_action.get_user_actions('0'),
                             [['Test Name', 'simple_task', 'test text', time.strftime("%H:%M:%S", self.time)]])

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_no_command(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        with patch('auxiliary_functions.db_user_action', new=self.db):
            simple_task(None)
            self.assertEqual(auxiliary_functions.db_user_action.get_user_actions('0'), [])

    def tearDown(self) -> None:
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.UserDataBase()
            self.update = unittest.mock.MagicMock()


class TestDatabaseOldFunctions(unittest.TestCase):

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def setUp(self) -> None:
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.UserDataBase()

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_get_list_actions(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        self.db.add_user_action(user_id='111', user_action=get_action())
        with patch('auxiliary_functions.db_user_action', new=self.db):
            self.assertEqual(auxiliary_functions.get_list_actions('111'), [[value for value in get_action().values()]])

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_get_csv_from_db(self):
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.CsvDataBase()
        self.db.db_covid_csv = pymongo.MongoClient('testserver.com')['covid_csv']
        self.db.db_covid_csv['01.01.01'].insert_one({"test": "test"})
        with patch('auxiliary_functions.db_csv_files', new=self.db):
            self.assertEqual(auxiliary_functions.get_csv_from_db('01.01.01'), {"test": "test"})

    @mongomock.patch(servers=(('testserver.com', 27017),))
    @patch.object(database.pandas, 'read_csv', lambda self: get_dataframe())
    def test_add_date_to_db(self):
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.CsvDataBase()
        self.db.db_covid_csv = pymongo.MongoClient('testserver.com')['covid_csv']
        with patch('auxiliary_functions.db_csv_files', new=self.db):
            auxiliary_functions.add_date_to_db('01.01.02')
            self.assertEqual(auxiliary_functions.get_csv_from_db('01.01.02'), {'Admin2': {'0': 'Abbeville'},
                                                                               'Country_Region': {'0': 'US'},
                                                                               'FIPS': {'0': '45001'},
                                                                               'Province_State': {
                                                                                   '0': 'South Carolina'}})

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_no_dates(self):
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.CsvDataBase()
        self.db.db_covid_csv = pymongo.MongoClient('testserver.com')['covid_csv']
        with patch('auxiliary_functions.db_csv_files', new=self.db):
            self.assertFalse(auxiliary_functions.check_exist_dates('0'))

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_exist_dates(self):
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.CsvDataBase()
        self.db.db_covid_csv = pymongo.MongoClient('testserver.com')['covid_csv']
        self.db.db_covid_csv['1'].insert_one({'Test': 'test'})
        with patch('auxiliary_functions.db_csv_files', new=self.db):
            self.assertTrue(auxiliary_functions.check_exist_dates('1'))

    def tearDown(self) -> None:
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.UserDataBase()


class TestImageHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.update = unittest.mock.MagicMock()
        self.bot = unittest.mock.MagicMock()

    @patch.object(auxiliary_functions.ChatAction, 'UPLOAD_PHOTO',
                  lambda self: simple_action())
    def test_image_decorator(self):
        self.update.message.chat_id = 0
        self.update.message.reply_text.return_value = None
        self.bot.send_chat_action.return_value = None
        self.bot.send_photo.return_value = None
        '''with patch('auxiliary_functions.bot', new=self.bot):
            with self.assertRaises(FileNotFoundError):
                simple_image(self.update)'''
        pass
