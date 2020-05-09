import requests
from bs4 import BeautifulSoup

import pandas as pd
import folium
import matplotlib.pyplot as plt
from auxiliary_functions import check_exist_dates, get_csv_from_db, add_date_to_db
from datetime import datetime, timedelta
import numpy as np
from scipy.spatial.distance import cosine
import re

"""This class contains two class. You can look at world covid stat or region covid stat"""


class CovidRegionStat:
    def __init__(self):
        self._all_regions = CovidRegionStat.get_regions_information()
        self._user_id_file = 0
        self._name_data_frame = ''
        self._path_csv_file = ''
        self._path_plot_file = ''
        self._matrix = []
        self._russian_alphabet = {chr(symbol): key for key, symbol in zip(range(33), range(ord('а'), ord('а') + 32))}
        self._result_alphabet = np.zeros((len(self._all_regions), len(self._russian_alphabet)))

    def transform_into_np_vector(self, region):
        np_vector = np.zeros(len(self._russian_alphabet))
        for symbol in str(region).lower():
            if symbol.isalpha():
                key = self._russian_alphabet[symbol]
                np_vector[key] += 1
        return np_vector

    def get_result_alphabet(self):
        for region, i in zip(self.get_list_of_regions(), range(len(self.get_list_of_regions()))):
            vector = self.transform_into_np_vector(region)
            self._result_alphabet[i] = vector
        return self._result_alphabet

    @staticmethod
    def get_cosine(one_vector, two_vector):
        res = []
        for i in range(0, len(two_vector)):
            res.append((i, (cosine(one_vector, two_vector[i]))))
        return res

    def get_path_to_plot_file(self):
        return self._path_plot_file

    def get_list_of_regions(self) -> list:
        return list(self._all_regions.keys())

    def get_specific_region_by_index(self, index):
        for region, idx in zip(self._all_regions, range(len(self._all_regions))):
            if idx == index:
                return region

    def get_specific_region_href(self, region_name) -> str:
        if region_name in self._all_regions:
            return self._all_regions[region_name]

        raise Exception("Don't exist a such region")

    @staticmethod
    def get_regions_information():
        get = requests.get('https://coronavirusstat.ru/country/russia/')
        if get.status_code != 200:
            return None

        page = BeautifulSoup(get.content, 'lxml')
        all_region = page.find_all('div', {'class': 'row border border-bottom-0 c_search_row'})
        regions = {}

        for region in all_region:
            try:
                region = region.find('a')
                name_region = region.get_text()
                href_region = region['href']
                regions[name_region] = 'https://coronavirusstat.ru' + href_region
            except:  # noqa: E722  # TODO: will fix this later
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
        plt.plot(date, confirmed, label="Confirmed")
        plt.plot(date, confirmed, 'bo')
        plt.plot(date, new_confirmed, label="New confirmed for day")
        plt.legend()
        self._path_plot_file = f'corona_information/{self._name_data_frame}_{self._user_id_file}.jpg'
        plt.savefig(self._path_plot_file)


class CovidWorldStat:

    def __init__(self):
        self.today_date = ''
        self.yesterday_date = ''
        self.today_df = ''
        self.yesterday_df = ''

    def set_date(self, days_ago):
        date_format = '%m-%d-%Y'
        today = datetime.now() - timedelta(days=days_ago)
        yesterday = datetime.now() - timedelta(days=days_ago + 1)
        self.today_date = today.strftime(date_format)
        self.yesterday_date = yesterday.strftime(date_format)

    def set_user_date(self, date):
        date = re.sub(r'[/ -.]', '-', date)

        date = self.check_user_date_mdy(date)
        if not date:
            raise Exception("Enter correct date mm-dd-yy")

        date_format = '%m-%d-%Y'

        date = datetime.strptime(date, date_format)

        yesterday = date - timedelta(1)

        self.today_date = date.strftime(date_format)
        self.yesterday_date = yesterday.strftime(date_format)

    @staticmethod
    def check_user_date_mdy(date: str) -> str:
        date = re.match(r'^((0[1-9]|1[012])[/ -.](0[1-9]|[12][0-9]|3[01])[/ -.]\d{4})$', date)

        if date:
            return date.group(0)

    def set_data_frame(self):
        self.today_df = self.get_data_frame(self.today_date)
        self.yesterday_df = self.get_data_frame(self.yesterday_date)

    def get_difference_disease(self, top=5) -> list:

        today_df = self.today_df
        yesterday_df = self.yesterday_df

        province_state = 'Province_State'
        try:
            today_df[province_state]
        except:
            province_state = 'Province/State'

        today_df = today_df.sort_values(by=[province_state]).reset_index(drop=True)  # Reset all indexes
        yesterday_df = yesterday_df.sort_values(by=[province_state]).reset_index(drop=True)  # Reset all indexes
        yesterday_df = yesterday_df.append(today_df[~today_df[province_state].isin(yesterday_df[province_state])])
        yesterday_df = yesterday_df.sort_values(by=[province_state]).reset_index(drop=True)
        today_df['Confirmed'] = today_df['Confirmed'] - yesterday_df['Confirmed']  # Get count confirmed
        today_df.loc[
            today_df['Confirmed'] < 0] *= -1  # If new entry, it'll be less than zero, 'cause we need to change it
        today_df = today_df[today_df['Confirmed'] > 0]
        today_df = today_df.sort_values(by=['Confirmed'], ascending=False)

        place = 1
        top_covid_places = []
        for i in today_df.index:
            if top + 1 == place:
                break
            if today_df[province_state][i] != '':

                try:
                    temp = today_df['Combined_Key'][i]
                except:
                    temp = today_df[province_state][i]
                output = f"<b>{place}</b>  {temp} - {today_df['Confirmed'][i]}\n"
                place += 1
                top_covid_places.append(output)
        CovidWorldStat.get_covid_map(data_frame=today_df)  # Get map with sick

        return top_covid_places

    @staticmethod
    def get_data_frame(date):
        if not check_exist_dates(date):
            add_date_to_db(date)
        csv_content = get_csv_from_db(date)
        return pd.DataFrame(csv_content).dropna()

    @staticmethod
    def get_covid_map(data_frame):
        maps = folium.Map(location=[43.01093752182322, 11.903098859375019], zoom_start=2.4, tiles='Stamen Terrain')
        """Creating map"""
        for i in data_frame.index:
            try:
                if data_frame['Confirmed'][i] >= 1000:
                    color = 'red'
                elif 500 <= data_frame['Confirmed'][i] <= 1000:
                    color = 'orange'
                else:
                    continue
                if data_frame['Province_State'][i] == '':
                    continue
                folium.Marker(location=[data_frame['Lat'][i], data_frame['Long_'][i]],
                              popup=f"{data_frame['Province_State'][i]}:{data_frame['Confirmed'][i]}",
                              icon=folium.Icon(color=color, icon='info-sign')).add_to(maps)
            except:  # noqa: E722  # TODO: will fix this later
                maps.save('corona_information/map.html')
        maps.save('corona_information/map.html')
