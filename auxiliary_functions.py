import time
from telegram import ChatAction, Bot
from setup import TOKEN, PROXY
import pymongo
import pandas

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


# USERS_ACTION = []
# ACTION_COUNT = 0

client = pymongo.MongoClient()

db_user_actions = client['user_actions']
db_covid_csv = client['covid_csv']


def handle_command(func):
    def inner(*args, **kwargs):
        update = args[0]
        if update:
            user_action = {
                'user_name': update.effective_user.first_name,
                'function': func.__name__,
                'text': update.message.text,
                'time': time.strftime("%H:%M:%S", time.localtime())
            }
            id_user = str(update.message.chat_id)
            db_user_actions[id_user].insert_one(user_action)
        return func(*args, **kwargs)
    return inner


def get_list_actions(chat_id: str) -> list:
    actions = []
    for action in db_user_actions[chat_id].find():
        actions.append([action['user_name'], action['function'], action['text'], action['time']])
    return actions


def check_exist_dates(date):
    if db_covid_csv[date].find_one() is None:
        return False
    return True


def get_csv_from_db(date):
    csv_content = db_covid_csv[date].find_one()
    del csv_content['_id']
    return csv_content


def add_date_to_db(date):
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

    db_covid_csv[date].insert_one(s)


def handle_image(func):
    """Decorator for image_handler
        This function uploading image for user and calling image handler method"""

    def inner(*args, **kwargs):
        update = args[0]
        bot.send_chat_action(chat_id=update.message.chat_id,
                             action=ChatAction.UPLOAD_PHOTO)
        update.message.reply_text("Processing...")
        func(*args, **kwargs)
        bot.send_photo(chat_id=update.message.chat_id,
                       photo=open("result_user_images/res.jpg", mode='rb'))
    return inner
