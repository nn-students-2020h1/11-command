import unittest
import requests
import os


"""Useful tests"""


class HomeWorkTest(unittest.TestCase):

    def test_internet_connection(self):
        """Have we access to internet?"""

        self.assertTrue(requests.get('https://yandex.ru/news/rubric/koronavirus?from=region'))
        self.assertTrue(requests.get('https://github.com/'
                                     'CSSEGISandData/COVID-19/tree/master/'
                                     'csse_covid_19_data/csse_covid_19_daily_reports'))
        self.assertTrue(requests.get('https://cat-fact.herokuapp.com/facts'))

    def test_exist_unnecessary_files(self):
        """Have we unnecessary files in folders?"""

        path = os.path.abspath(os.curdir)

        path = path.replace('tests', 'initial_user_images')
        self.assertFalse(len(os.listdir(path)))
        path = path.replace('initial_user_images', 'result_user_images')
        self.assertFalse(len(os.listdir(path)))
        path = path.replace('result_user_images', 'corona_information')
        self.assertFalse(len(os.listdir(path)))


if __name__ == "__main__":
    unittest.main()
