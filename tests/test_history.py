import unittest
from unittest.mock import patch
import sys
import pymongo
import mongomock
import pandas as pd
import database


def get_action():
    return {
        'user_name': 'Test Name',
        'function': 'Test Get Actions',
        'text': 'Action got successfully',
        'time': '14:35:44'
    }


def get_dataframe():
    test_data = [['45001', 'Abbeville', 'South Carolina', 'US']]
    test_dataframe = pd.DataFrame(test_data, columns=['FIPS', 'Admin2', 'Province_State', 'Country_Region'])
    return test_dataframe


class TestLoadHistory(unittest.TestCase):
    @mongomock.patch(servers=(('testserver.com', 27017),))
    def setUp(self):
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.UserDataBase()

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_get_actions(self):
        self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
        self.db.add_user_action(user_id='111', user_action=get_action())
        self.assertEqual(self.db.get_user_actions(user_id='111'), [[value for value in get_action().values()]])

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_get_empty_history(self):
        self.assertEqual(self.db.get_user_actions(user_id='0'), [])

    def tearDown(self):
        self.db = database.UserDataBase()


class TestCSV(unittest.TestCase):
    @mongomock.patch(servers=(('testserver.com', 27017),))
    def setUp(self):
        with patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.CsvDataBase()
        self.db.db_covid_csv = pymongo.MongoClient('testserver.com')['covid_csv']

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_no_data(self):
        self.assertFalse(self.db.check_exist_dates('0'))

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_csv_from_db(self):
        self.db.db_covid_csv['01.01.01'].insert_one({"test": "test"})
        self.assertEqual(self.db.get_csv_from_db('01.01.01'), {"test": "test"})

    @mongomock.patch(servers=(('testserver.com', 27017),))
    @patch.object(database.pandas, 'read_csv', lambda self: get_dataframe())
    def test_add_csv_to_db(self):
        self.db.add_data_frame('01.01.02')
        self.assertEqual(self.db.get_csv_from_db('01.01.02'), {'Admin2': {'0': 'Abbeville'},
                                                               'Country_Region': {'0': 'US'},
                                                               'FIPS': {'0': '45001'},
                                                               'Province_State': {
                                                                   '0': 'South Carolina'}})

    def tearDown(self):
        self.db = database.CsvDataBase()
