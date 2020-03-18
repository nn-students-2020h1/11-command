#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import json
import os
import requests
import image_handler as img_h
from setup import PROXY, TOKEN
from telegram import Bot, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

USERS_ACTION = []
USER_ACTIONS_FILE = "user_actions.json"
IMAGE_PATH = "ing.jpg"


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
        return func(*args, **kwargs)
    return inner

@handle_command
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    try:
        load_history(update)
    except FileNotFoundError:
        f = open(f"{update.message.chat.id}.json", "w+")
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')

@handle_command
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи команду /start для начала. ')

@handle_command
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def save_history(update: Update):
    with open(f"{update.message.chat.id}.json", mode="w", encoding="utf-8") as handle:
        json.dump(USERS_ACTION, handle, ensure_ascii=False, indent=2)

def load_history(update: Update):
    global USERS_ACTION
    if os.stat(f"{update.message.chat.id}.json").st_size == 0:
        return
    with open(f"{update.message.chat.id}.json", mode="r", encoding="utf-8") as handle:
        USERS_ACTION = json.load(handle)

@handle_command
def history(update: Update, context: CallbackContext):
    """Display 5 latest ACTION_HISTORY elements when the command /history is issued."""
    save_history(update)
    update.message.reply_text("Last 5 actions:")
    with open(f"{update.message.chat.id}.json", "r") as handle:
        data = json.load(handle)
        output = ""
        for action in data:
            for key, value in action.items():
                output += f"{key}: {value}\n"
            output += "\n"
        update.message.reply_text(output)

@handle_command
def fact(update: Update, context: CallbackContext):
    fact = requests.get("https://cat-fact.herokuapp.com/facts").json()["all"][0]
    quote = f"<i>{fact['text']}</i>"
    author = f"<b>Author: {fact['user']['name']['first']} {fact['user']['name']['last']}</b>"
    update.message.reply_text("Well, time for a good quote...")
    update.message.reply_text(f'«{quote}»\n\t                     一 {author:}', parse_mode=telegram.ParseMode.HTML)

@handle_command
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')

@handle_command
def get_image(update: Update, context: CallbackContext):
    """This method getting an image and give choice to user
            what to do with image"""
    file = update.message.photo[-1].file_id
    image = bot.get_file(file)
    image.download('initial.jpg')
    custom_keyboard = [
        ["/example"]
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text="You need to choice any method",
                     reply_markup=reply_markup)

def handle_image(func):
    """Decorator for image_handler
        This function uploading image for user and calling image handler method"""
    def inner(*args, **kwargs):
        update = args[0]
        update.message.reply_text("Processing...")
        func(*args, **kwargs)
        bot.send_photo(chat_id=update.message.chat_id, photo=open("res.jpg", mode='rb'))
        update.message.reply_text("Your image!")
    return inner


@handle_image
@handle_command
def handle_img_blk_wht(update: Update, context: CallbackContext):
    img_h.get_black_white_img()


def handle_image(func):
    """Decorator for image_handler
        This function uploading image for user and calling image handler method"""
    def inner(*args, **kwargs):
        update = args[0]
        update.message.reply_text("Processing...")
        func(*args, **kwargs)
        bot.send_photo(chat_id=update.message.chat_id, photo=open("res.jpg", mode='rb'))
        update.message.reply_text("Your image!")
    return inner


@handle_image
@handle_command
def handle_img_blk_wht(update: Update, context: CallbackContext):
    img_h.get_black_white_img()


def main():
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))
    updater.dispatcher.add_handler(CommandHandler('example', handle_img_blk_wht))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, get_image))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    updater.dispatcher.add_error_handler(error)
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Start Bot')
    main()