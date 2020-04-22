import json
import time
import os
from telegram import Update, ChatAction, Bot
from setup import TOKEN, PROXY


bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


USERS_ACTION = []
ACTION_COUNT = 0


def handle_command(func):
    def inner(*args, **kwargs):
        global ACTION_COUNT
        update = args[0]
        if update:
            if USERS_ACTION.__len__() > 4:
                USERS_ACTION.pop(0)
            USERS_ACTION.append({
                'user_name': update.effective_user.first_name,
                'function': func.__name__,
                'text': update.message.text,
                'time': time.strftime("%H:%M:%S", time.localtime())
            })
            save_history(update=update)
        return func(*args, **kwargs)
    return inner


def load_history(update: Update):
    """Upload user's history"""
    global USERS_ACTION
    try:
        if os.stat(f"user_history/{update.message.chat.id}.json").st_size == 0:
            return None
    except FileNotFoundError:
        return None
    with open(f"{update.message.chat.id}.json", mode="r", encoding="utf-8") as handle:  # opening file named user ID
        USERS_ACTION = json.load(handle)  # getting the user actions from file


def save_history(update: Update):
    """Save user's history"""
    with open(f"user_history/{update.message.chat.id}.json",
              mode="w", encoding="utf-8") as handle:  # opening file named user ID
        json.dump(USERS_ACTION, handle, ensure_ascii=False, indent=2)  # uploading actions to the file


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


