import requests
from bs4 import BeautifulSoup

import pandas as pd
import folium
import matplotlib.pyplot as plt
from auxiliary_functions import check_exist_dates, get_csv_from_db, add_date_to_db
from datetime import datetime, timedelta

"""This class contains two class. You can look at world covid stat or region covid stat"""


class CovidRegionStat:
    def __init__(self):
        self._all_regions = CovidRegionStat.get_regions_information()
        self._user_id_file = 0
        self._name_data_frame = ''
        self._path_csv_file = ''
        self._path_plot_file = ''

    def get_path_to_plot_file(self):
        return self._path_plot_file

    def get_list_of_regions(self) -> list:
        return list(self._all_regions.keys())

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
        plt.plot(date, confirmed, label="Confirmed")
        plt.plot(date, confirmed, 'bo')
        plt.plot(date, new_confirmed, label="New confirmed for day")
        plt.legend()
        self._path_plot_file = f'corona_information/{self._name_data_frame}_{self._user_id_file}.jpg'
        plt.savefig(self._path_plot_file)


class CovidWorldStat:

    def __init__(self):

        self.today_date, self.yesterday_date = CovidWorldStat.set_date(days_ago=1)

        self.today_df = self.get_data_frame(self.today_date)
        self.yesterday_df = self.get_data_frame(self.yesterday_date)

    @staticmethod
    def set_date(days_ago=0):
        date_format = '%m-%d-%Y'
        today = datetime.now() - timedelta(days=days_ago)
        yesterday = today - timedelta(days=days_ago - 1)
        return today.strftime(date_format), yesterday.strftime(date_format)

    def get_today_df(self):
        return self.today_df

    def get_yesterday_df(self):
        return self.yesterday_df

    @staticmethod
    def get_difference_disease(today_df: pd.DataFrame, yesterday_df: pd.DataFrame, top=5) -> list:

        today_df = today_df.sort_values(by=['Province_State']).reset_index(drop=True)  # Reset all indexes
        yesterday_df = yesterday_df.sort_values(by=['Province_State']).reset_index(drop=True)  # Reset all indexes
        yesterday_df = yesterday_df.append(today_df[~today_df['Province_State'].isin(yesterday_df['Province_State'])])
        yesterday_df = yesterday_df.sort_values(by=['Province_State']).reset_index(drop=True)
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
            if today_df['Province_State'][i] != '':
                output = f"<b>{place}</b>  {today_df['Combined_Key'][i]} - {today_df['Confirmed'][i]}\n"
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
                folium.Marker(location=[data_frame['Lat'][i], data_frame['Long_'][i]],
                              popup=f"{data_frame['Province_State'][i]}:{data_frame['Confirmed'][i]}",
                              icon=folium.Icon(color=color, icon='info-sign')).add_to(maps)
            except:
                maps.save('corona_information/map.html')
        maps.save('corona_information/map.html')
