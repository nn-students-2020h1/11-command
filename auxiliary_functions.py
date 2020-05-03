import time
from telegram import ChatAction, Bot
from setup import TOKEN, PROXY
from database import UserDataBase, CsvDataBase

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


# USERS_ACTION = []
# ACTION_COUNT = 0
db_user_action = UserDataBase()
db_csv_files = CsvDataBase()


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
            db_user_action.add_user_action(id_user, user_action)
        return func(*args, **kwargs)
    return inner


def get_list_actions(chat_id: str) -> list:
    return db_user_action.get_user_actions(chat_id)


def get_csv_from_db(date: str):
    return db_csv_files.get_csv_from_db(date)


def add_date_to_db(date):
    db_csv_files.add_data_frame(date)


def check_exist_dates(date: str):
    return db_csv_files.check_exist_dates(date)


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
