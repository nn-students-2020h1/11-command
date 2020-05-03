import pymongo
import pandas


class UserDataBase:

    def __init__(self):
        self.client = pymongo.MongoClient()

        self.db_user_actions = self.client['user_actions']

    def add_user_action(self, user_id: str, user_action: dict):
        self.db_user_actions[user_id].insert_one(user_action)

    def get_user_actions(self, user_id: str) -> list:
        actions = []
        for action in self.db_user_actions[user_id].find():
            actions.append([action['user_name'], action['function'], action['text'], action['time']])
        return actions


class CsvDataBase:

    def __init__(self):
        self.client = pymongo.MongoClient()
        self.db_covid_csv = self.client['covid_csv']

    def check_exist_dates(self, date: str):
        if self.db_covid_csv[date].find_one() is None:
            return False
        return True

    def get_csv_from_db(self, date: str):
        csv_content = self.db_covid_csv[date].find_one()
        del csv_content['_id']
        return csv_content

    def add_data_frame(self, date: str):
        s = pandas.read_csv("https://raw.githubusercontent.com/"
                            "CSSEGISandData/COVID-19/master/csse_covid_19_data/"
                            f"csse_covid_19_daily_reports/{date}.csv")
        csv_dict = s.to_dict()
        s = {}

        for keys, values in csv_dict.items():
            s[keys] = 0
            temp = {}
            for key, value in values.items():
                temp_key = str(key)
                temp[temp_key] = value
            s[keys] = temp

        self.db_covid_csv[date].insert_one(s)


