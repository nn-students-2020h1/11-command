import unittest
from unittest import mock

from covid_news import CovidNews


class TestCovidNews(unittest.TestCase):

    def setUp(self) -> None:
        self.item = mock.MagicMock()
        self.bs_news_page = mock.MagicMock()

    @mock.patch("covid_news.CovidNews.parse_news_page")
    @mock.patch("covid_news.CovidNews.make_request_news")
    def test_get_news(self, mock_make_request, mock_parse_news_page):
        mock_status_200 = mock.Mock(status_code=200)  # check download html

        mock_make_request.return_value = mock_status_200

        self.bs_news_page.__iter__.return_value = [self.item]  # Create iter object
        mock_parse_news_page.return_value = self.bs_news_page

        content = CovidNews.get_news()

        self.assertIsInstance(content, dict)
        self.assertTrue(mock_make_request)
        self.assertGreater(len(content), 0)


if __name__ == '__main__':
    unittest.main()
