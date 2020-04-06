import requests
from bs4 import BeautifulSoup

from random import shuffle
import inline_handle


class CovidNews:
    def __init__(self):
        self._news_information = CovidNews.get_news()  # Fill dictionary fresh information
        self._title_list = list(self._news_information.keys())  # Create list of news titles
        self._current_news = 0

    def send_message(self, bot, chat_id, value):
        temp = bot.send_message(chat_id=chat_id,
                                text=f"<b><u>{self.get_title_news(number=value)}</u></b> "
                                f"\n\n{self.get_brief_description(number=value)}",
                                parse_mode='HTML')

        self.set_current_news(value)
        bot.delete_message(chat_id, temp.message_id - 1)
        bot.send_message(chat_id=chat_id,
                         text="Do you want to read more?",
                         reply_markup=inline_handle.InlineKeyboardFactory.get_inline_keyboard_more_information())

    def set_current_news(self, value):
        self._current_news = value

    def shuffle_news(self):  # Shuffle all the news in list
        shuffle(self._title_list)

    def get_title_news(self, number):  # Get title of specific news
        return self._title_list[number]

    def get_brief_description(self, number):  # Get brief description certain news
        """Title of news is dictionary key, thus search for specific news will be in constant time O(1)
        because collision won't be, one news corresponds to specif link """
        return self._news_information[self.get_title_news(number)][1]

    def get_href_news(self):  # Get link of specific news
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
