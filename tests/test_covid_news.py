import unittest
from unittest import mock
from unittest.mock import patch

from covid_news import CovidNews


class TestCovidNews(unittest.TestCase):

    def setUp(self) -> None:
        self.item = mock.MagicMock()
        self.bs_news_page = mock.MagicMock()

    @mock.patch("covid_news.CovidNews.parse_news_page")
    @mock.patch("covid_news.CovidNews.make_request_news")
    def test_empty_get_news(self, mock_make_request, mock_parse_news_page):
        mock_status_200 = mock.Mock(status_code=200)  # check download html

        mock_make_request.return_value = mock_status_200

        self.bs_news_page.__iter__.return_value = [self.item]  # Create iter object
        mock_parse_news_page.return_value = self.bs_news_page

        content = CovidNews.get_news()

        self.assertIsInstance(content, dict)
        self.assertGreater(len(content), 0)

    def test_download_page_get_news(self):
        with patch("covid_news.CovidNews.make_request_news") as mock_response:
            mock_response.status_code.return_value = 404
            with self.assertRaises(Exception) as context:
                CovidNews.get_news()
            self.assertTrue("html page wasn't downloaded" in str(context.exception))

    def test_get_title_is_str(self):
        with patch('covid_news.CovidNews.get_title_news') as mock_title:
            mock_title.return_value = "Putin"
            self.assertIsInstance(CovidNews.get_title_news(index=0), str)

    def test_get_title_is_equal(self):
        with patch('covid_news.CovidNews.get_title_news') as mock_title:
            mock_title.return_value = "Donald Trump is president"
            self.assertEqual(CovidNews.get_title_news(index=0), "Donald Trump is president")

    def test_get_brief_description_is_str(self):
        with patch('covid_news.CovidNews.get_brief_description') as mock_description:
            mock_description.return_value = "Some text"
            self.assertIsInstance(CovidNews.get_brief_description(index=0), str)

    def test_get_brief_description_is_equal(self):
        with patch('covid_news.CovidNews.get_brief_description') as mock_description:
            mock_description.return_value = "Some very large text"*500000
            self.assertEqual(CovidNews.get_brief_description(index=0), "Some very large text"*500000)


if __name__ == '__main__':
    unittest.main()
