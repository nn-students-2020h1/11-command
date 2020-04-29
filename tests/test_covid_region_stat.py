import unittest
from unittest.mock import patch
from unittest import mock

from covid_stat import CovidRegionStat


class TestCovidRegionStat(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_get_list_of_regions_is_list(self):
        with patch("covid_stat.CovidRegionStat.get_list_of_regions") as mock_list:
            mock_list.return_value = list(range(1))
            self.assertIsInstance(CovidRegionStat.get_list_of_regions(), list)

    def test_get_list_of_regions_not_empty(self):
        with patch("covid_stat.CovidRegionStat.get_list_of_regions") as mock_list:
            mock_list.return_value = list(range(1))
            self.assertGreater(len(CovidRegionStat.get_list_of_regions()), 0)

    def test_get_path_to_plot_file_is_str(self):
        with patch("covid_stat.CovidRegionStat.get_path_to_plot_file") as mock_path:
            mock_path.return_value = "/path_to_plot_file"
            self.assertIsInstance(CovidRegionStat.get_path_to_plot_file(), str)

    def test_get_path_to_plot_file_not_empty(self):
        with patch("covid_stat.CovidRegionStat.get_path_to_plot_file") as mock_path:
            mock_path.return_value = "corona_information/name.jpg"
            self.assertIn('.jpg', CovidRegionStat.get_path_to_plot_file())
            self.assertIn('corona_information/', CovidRegionStat.get_path_to_plot_file())

    def test_get_specific_refion_href_is_str(self):
        with patch("covid_stat.CovidRegionStat.get_path_to_plot_file") as mock_href:
            mock_href.return_value = "google.com"
            testStat = CovidRegionStat()
            self.assertIsInstance(CovidRegionStat.get_specific_region_href(testStat, region_name="Москва"), str)

    @patch('covid_stat.CovidRegionStat.get_specific_region_href')
    def test_get_specific_refion_href(self, mock_href):
        mock_region_name = mock.Mock()
        mock_region_name.return_value = 0
        mock_href.return_value = mock_region_name
        mock_href.side_effect = Exception
        with self.assertRaises(Exception):
            CovidRegionStat.get_specific_region_href(mock_region_name)
