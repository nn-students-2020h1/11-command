import json
import time
import os
from telegram import Update, ChatAction, Bot
from setup import TOKEN, PROXY
import pymongo

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


# USERS_ACTION = []
# ACTION_COUNT = 0

client = pymongo.MongoClient()
db_user_actions = client['user_actions']


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

# def load_history(update: Update):
#     """Upload user's history"""
#     global USERS_ACTION
#     try:
#         if os.stat(f"user_history/{update.message.chat.id}.json").st_size == 0:
#             return None
#     except FileNotFoundError:
#         return None
#     with open(f"{update.message.chat.id}.json", mode="r", encoding="utf-8") as handle:  # opening file named user ID
#         USERS_ACTION = json.load(handle)  # getting the user actions from file
#
#
# def save_history(update: Update):
#     """Save user's history"""
#     with open(f"user_history/{update.message.chat.id}.json",
#               mode="w", encoding="utf-8") as handle:  # opening file named user ID
#         json.dump(USERS_ACTION, handle, ensure_ascii=False, indent=2)  # uploading actions to the file


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


