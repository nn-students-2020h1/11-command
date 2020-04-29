import requests
from bs4 import BeautifulSoup

from random import shuffle


class CovidNews:
    """This class creates inline_keyboard with news from www.yandex.ru about covid-19,
    you can choose to read more about specific news or get link to source or get other news"""

    def __init__(self):
        self._news_information = CovidNews.get_news()  # Fill dictionary fresh information
        self._title_list = list(self._news_information.keys())  # Create list of news titles
        self._current_news = 0

    def send_message(self, bot, chat_id, value):
        temp = bot.send_message(chat_id=chat_id,
                                text=f"<b><u>{self.get_title_news(index=value)}</u></b> "
                                f"\n\n{self.get_brief_description(index=value)}",
                                parse_mode='HTML')

        self.set_current_news(value)
        bot.delete_message(chat_id, temp.message_id - 1)

    def set_current_news(self, value: int):
        self._current_news = value

    def shuffle_news(self):  # Shuffle all the news in list
        shuffle(self._title_list)

    def get_title_news(self, index: int) -> str:  # Get title of specific news
        return self._title_list[index]

    def get_brief_description(self, index: int) -> str:  # Get brief description certain news
        """Title of news is dictionary key, thus search for specific news will be in constant time O(1)
        because collision won't be, one news corresponds to specif link """
        return self._news_information[self.get_title_news(index)][1]

    def get_href_news(self) -> str:  # Get link of specific news
        return self._news_information[self.get_title_news(self._current_news)][0]

    @staticmethod
    def make_request_news():
        return requests.get("https://yandex.ru/news/rubric/koronavirus?from=region")

    @staticmethod
    def parse_news_page(news_page):
        bs_news_page = BeautifulSoup(news_page, 'lxml')  # Parse this web image
        return bs_news_page.find_all('div', {'class': 'story story_view_normal story_notags story_noimage'})

    @staticmethod
    def get_news() -> dict:
        content = {}
        news_page = CovidNews.make_request_news()  # Get html page with news

        if news_page.status_code != 200:
            raise Exception("html page wasn't downloaded")

        bs_news_page = CovidNews.parse_news_page(news_page=news_page.content)

        for item in bs_news_page:
            title = item.find('a').get_text()  # Get title of news
            href = item.find('a').get('href')  # Get href to news
            brief_news = item.find('div', {'class': 'story__text'}).get_text()  # Get a brief description of news
            content[title] = ['https://yandex.ru' + href, brief_news]  # Add into dict\

        return content  # Return dict of news
