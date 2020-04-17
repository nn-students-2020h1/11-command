import requests
from bs4 import BeautifulSoup

from random import shuffle
import inline_handle
import pandas as pd
import matplotlib.pyplot as plt


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


class CovidStat:
    def __init__(self):
        self._all_regions = CovidStat.get_regions_information()
        self._user_id_file = 0
        self._name_data_frame = ''
        self._path_csv_file = ''
        self._path_plot_file = ''

    def get_path_to_plot_file(self):
        return self._path_plot_file

    def get_list_of_regions(self):
        return list(self._all_regions.keys())

    def get_specific_region_href(self, region_name):
        try:
            return self._all_regions[region_name]
        except RuntimeError:
            return None

    @staticmethod
    def get_regions_information():
        get = requests.get('https://coronavirusstat.ru/country/russia/')
        if get.status_code != 200:
            return None

        page = BeautifulSoup(get.content, 'lxml')

        all_region = page.find_all('div', {'class': 'row border border-bottom-0'})

        regions = {}

        for region in all_region:
            try:
                region = region.find('a')
                name_region = region.get_text()
                href_region = region['href']
                regions[name_region] = 'https://coronavirusstat.ru' + href_region
            except:
                break
        return regions

    def get_and_save_csv_table(self, href_by_region, user_id):
        get = requests.get(href_by_region)
        if get.status_code != 200:
            return None

        page = BeautifulSoup(get.content, 'lxml')

        page = page.find('table', {'class': 'table table-bordered small'})

        table_body = page.find_all('tr')
        result = []
        for row in table_body:
            date = row.find('th').text
            cols = row.find_all('td')

            cols = [element.text.split() for element in cols]
            cols.append(date)
            result.append(cols)
        result.pop(0)
        df = []

        for i in result:
            if '%' in i[0][1]:
                i[0][1] = 0
            temp = {'Date': str(i[4]).replace('.', '-').replace('-2020', ''), "Confirmed": i[0][0],
                    "New_confirmed": str(i[0][1]).replace('+', ''), "Recovered": i[1][0], "Dead": i[2][0]}
            df.append(temp)
        df = pd.DataFrame(df)

        self._user_id_file = user_id
        self._name_data_frame = href_by_region.replace('https://coronavirusstat.ru/country/', '')
        self._name_data_frame = href_by_region.replace('/', '')
        self._path_csv_file = f'corona_information/{self._name_data_frame}_{self._user_id_file}.csv'
        df.to_csv(self._path_csv_file)

    def get_plot_region(self):
        df = pd.read_csv(self._path_csv_file)
        date = df['Date'][::-1]
        confirmed = df['Confirmed'][::-1]
        new_confirmed = df['New_confirmed'][::-1]
        plt.xlabel("Time")
        plt.ylabel("Confirmed")
        plt.grid(which="major", linewidth=1)
        plt.plot(date, confirmed, 'bo', date, confirmed)
        plt.plot(date, new_confirmed)
        self._path_plot_file = f'corona_information/{self._name_data_frame}_{self._user_id_file}.jpg'
        plt.savefig(self._path_plot_file)
