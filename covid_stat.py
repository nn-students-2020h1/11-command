import requests
from bs4 import BeautifulSoup

import pandas as pd
import folium
import matplotlib.pyplot as plt

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
        self.link_yesterday = self.parse_html_page(self.make_corona_stat_request(), 3)
        self.link_today = self.parse_html_page(self.make_corona_stat_request(), 2)

        self.today_df = self.get_data_frame(self.link_today)
        self.yesterday_df = self.get_data_frame(self.link_yesterday)

    def get_today_df(self):
        return self.today_df

    def get_yesterday_df(self):
        return self.yesterday_df

    @staticmethod
    def get_difference_disease(today_df, yesterday_df, top=5):

        today_df = today_df.sort_values(by=['Province_State']).reset_index(drop=True)  # Reset all indexes
        yesterday_df = yesterday_df.append(today_df[~today_df['Province_State'].isin(yesterday_df['Province_State'])])
        yesterday_df = yesterday_df.sort_values(by=['Province_State']).reset_index(drop=True)
        today_df['Confirmed'] = today_df['Confirmed'] - yesterday_df['Confirmed']  # Get count confirmed
        today_df.loc[
            today_df['Confirmed'] < 0] *= -1  # If new entry, it'll be less than zero, 'cause we need to change it
        last_df = today_df[today_df['Confirmed'] > 0]
        last_df = last_df.sort_values(by=['Confirmed'], ascending=False)

        place = 1
        output = ''
        for i in last_df.index[:top]:
            if last_df['Province_State'][i] != '':
                output += f"<b>{place}</b> {last_df['Combined_Key'][i]} - {last_df['Confirmed'][i]}\n"
            place += 1
        CovidWorldStat.get_corona_map(data_frame=last_df)  # Get map with sick

        return output

    @staticmethod
    def parse_html_page(response, idx):
        soup = BeautifulSoup(response.content, 'lxml')  # Use library bs4

        return soup.find_all('tr', {'class': 'js-navigation-item'})[-idx]  # Get last csv

    @staticmethod
    def make_corona_stat_request():
        return requests.get('https://github.com/CSSEGISandData/'
                            'COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports')

    @staticmethod
    def get_data_frame(last_csv_url):
        response = requests.get("https://github.com/" + last_csv_url.find('a').get('href'))  # Open github page with csv
        csv_html = BeautifulSoup(response.content, 'lxml')
        csv_url = (csv_html.find('a', {'class': 'btn btn-sm BtnGroup-item'})).get('href')
        return pd.read_csv("https://github.com/" + csv_url).dropna()  # Open our csv file with pandas

    @staticmethod
    def get_corona_map(data_frame):
        maps = folium.Map(location=[43.01093752182322, 11.903098859375019], zoom_start=2.4, tiles='Stamen Terrain')
        """Creating map"""
        for i in data_frame.index.dropna():
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
