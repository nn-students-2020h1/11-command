import unittest
from unittest.mock import patch
import auxiliary_functions
import pymongo
import mongomock
import pandas as pd


def get_action():
    return {
        'user_name': 'Test Name',
        'function': 'Test Get Actions',
        'text': 'Action got successfully',
        'time': '14:35:44'
    }


class TestLoadHistory(unittest.TestCase):

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_get_actions(self):
        with patch("auxiliary_functions.db_user_actions",
                   new=pymongo.MongoClient('testserver.com')['user_actions']) as mock_db:
            mock_db['0'].insert_one(get_action())
            self.assertEqual(auxiliary_functions.get_list_actions('0'),
                             [['Test Name', 'Test Get Actions', 'Action got successfully', '14:35:44']])

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_get_empty_history(self):
        with patch("auxiliary_functions.db_user_actions",
                   new=pymongo.MongoClient('testserver.com')['user_actions']) as mock_db:
            self.assertEqual(auxiliary_functions.get_list_actions('0'), [])


class TestCSV(unittest.TestCase):
    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_data_exists(self):
        with patch("auxiliary_functions.db_covid_csv",
                   new=pymongo.MongoClient('testserver.com')['covid_csv']) as mock_db:
            mock_db['01.01.01'].insert_one({"test": "test"})
            self.assertTrue(auxiliary_functions.check_exist_dates('01.01.01'))

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_no_data(self):
        with patch("auxiliary_functions.db_covid_csv",
                   new=pymongo.MongoClient('testserver.com')['covid_csv']) as mock_db:
            self.assertFalse(auxiliary_functions.check_exist_dates('01.01.01'))

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_csv_from_db(self):
        with patch("auxiliary_functions.db_covid_csv",
                   new=pymongo.MongoClient('testserver.com')['covid_csv']) as mock_db:
            mock_db['01.01.01'].insert_one({"test": "test"})
            self.assertEqual(auxiliary_functions.get_csv_from_db('01.01.01'), {"test": "test"})

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_add_csv_to_db(self):
        with patch("auxiliary_functions.db_covid_csv",
                   new=pymongo.MongoClient('testserver.com')['covid_csv']) as mock_db:
            with patch('auxiliary_functions.pandas.read_csv') as mock_read_csv:
                test_data = [['45001', 'Abbeville', 'South Carolina', 'US']]
                test_dataframe = pd.DataFrame(test_data, columns=['FIPS', 'Admin2', 'Province_State', 'Country_Region'])
                mock_read_csv.return_value = test_dataframe
                auxiliary_functions.add_date_to_db('01.01.01')
                self.assertEqual(auxiliary_functions.get_csv_from_db('01.01.01'), {'Admin2': {'0': 'Abbeville'},
                                                                                   'Country_Region': {'0': 'US'},
                                                                                   'FIPS': {'0': '45001'},
                                                                                   'Province_State': {
                                                                                       '0': 'South Carolina'}})
