import unittest
from unittest import mock
from unittest.mock import patch

from covid_stat import CovidWorldStat
from pandas import DataFrame


class TestCovidWorldStat(unittest.TestCase):

    def test_make_corona_stat_request(self):
        with patch('covid_stat.CovidWorldStat.make_corona_stat_request') as mock_covid_request:
            mock_covid_request.return_value = 'is not  empty'
            self.assertTrue(CovidWorldStat.make_corona_stat_request())

    def test_get_data_frame_is_pandas_df(self):
        with patch('covid_stat.CovidWorldStat.get_data_frame') as mock_get_df:
            mock_get_df.return_value = DataFrame(columns=['one', 'two'])
            self.assertIsInstance(CovidWorldStat.get_data_frame(last_csv_url="url"), DataFrame)

    def test_get_data_frame_is_equal(self):
        with patch('covid_stat.CovidWorldStat.get_data_frame') as mock_get_df:
            mock_get_df.return_value = DataFrame(columns=['one', 'two'])
            df = DataFrame(columns=['one', 'two'])
            self.assertTrue(CovidWorldStat.get_data_frame('url').equals(df))

    def test_get_today_df_is_pandas_df(self):
        with patch('covid_stat.CovidWorldStat.get_today_df') as mock_today_df:
            mock_today_df.return_value = DataFrame(columns=['one', 'two'])
            self.assertIsInstance(CovidWorldStat.get_today_df(CovidWorldStat), DataFrame)

    def test_get_yesterday_df_is_pandas_df(self):
        with patch('covid_stat.CovidWorldStat.get_yesterday_df') as mock_yesterday_df:
            mock_yesterday_df.return_value = DataFrame(columns=['one', 'two'])
            self.assertIsInstance(CovidWorldStat.get_yesterday_df(CovidWorldStat), DataFrame)
