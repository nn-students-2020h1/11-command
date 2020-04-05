import requests
from bs4 import BeautifulSoup

from random import shuffle


class Covid19:
    def __init__(self):
        self._news_information = Covid19.get_news()
        self._title_list = list(self._news_information.keys())
        self._current_news = 0

    def set_current_news(self, value):
        self._current_news = value

    def shuffle_news(self):
        shuffle(self._title_list)

    def get_title_news(self, number):
        return self._title_list[number]

    def get_brief_description(self, number):
        return self._news_information[self.get_title_news(number)][1]

    def get_href_news(self):
        return self._news_information[self.get_title_news(self._current_news)][0]

    @staticmethod
    def get_news():
        content = {}
        news_page = requests.get("https://yandex.ru/news/rubric/koronavirus?from=region")  # Get html page with news
        news_page = BeautifulSoup(news_page.content, 'lxml')  # Parse this web image
        news_page = news_page.find_all('div', {'class': 'story story_view_normal story_notags story_noimage'})
        for item in news_page:
            title = item.find('a').get_text()  # Get title of news
            href = item.find('a').get('href')  # Get href to news
            brief_news = item.find('div', {'class': 'story__text'}).get_text()  # Get a brief description of news
            content[title] = ['https://yandex.ru' + href, brief_news]  # Add into map
        return content  # Return dict of news
