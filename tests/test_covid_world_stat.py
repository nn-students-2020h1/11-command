import unittest
from unittest.mock import patch

from covid_stat import CovidWorldStat
from pandas import DataFrame


class TestCovidWorldStat(unittest.TestCase):

    def setUp(self) -> None:
        self.test_df = DataFrame({"Confirmed": [1900, 500, 1, 10000],
                                  "Province_State": ["France", "Moscow", "Dublin", "Paris"],
                                  "Lat": [48.85341, 55.7522, 53.3331, 48.8534],
                                  "Long_": [2.3488, 37.6156, -6.24889, 2.3488]})

    def test_get_data_frame_is_pandas_df(self):
        with patch('covid_stat.CovidWorldStat.get_data_frame') as mock_get_df:
            mock_get_df.return_value = DataFrame(columns=['one', 'two'])
            self.assertIsInstance(CovidWorldStat.get_data_frame(last_csv_url="url"), DataFrame)

    def test_get_data_frame_is_equal(self):
        with patch('covid_stat.CovidWorldStat.get_data_frame') as mock_get_df:
            mock_get_df.return_value = DataFrame(columns=['one', 'two'])
            df = DataFrame(columns=['one', 'two'])
            self.assertTrue(CovidWorldStat.get_data_frame('url').equals(df))

    @patch('covid_stat.CovidWorldStat.get_difference_disease', return_value=list(range(5)))
    def test_mock_get_differ(self, mock_differ_disease):
        self.assertEqual(len(mock_differ_disease()), 5)


if __name__ == '__main__':
    unittest.main()
