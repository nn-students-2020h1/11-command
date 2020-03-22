#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import json
import os
import requests
import telegram
import time
import pandas as pd
import csv
import folium
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
import image_handler as img_h

from setup import PROXY, TOKEN
from telegram import Bot, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

USERS_ACTION = []
ACTION_COUNT = 0

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


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
        load_history(update)  # if file exists, load history (update for getting user ID)
    except FileNotFoundError:
        open(f"{update.message.chat.id}.json", "w+")  # if file doesn't exist, create it for a new user
    update.message.reply_text(f'Hi, {update.effective_user.first_name}!')
    update.message.reply_text('Please, type <b>/help</b> to see the list of commands.', parse_mode=telegram.ParseMode.HTML)


@handle_command
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Welcome! You're using the 11'th team bot.")
    update.message.reply_text("Type:\n<b>/start</b> to start the bot\n" +
                              "<b>/help</b> to get list of commands\n" +
                              "<b>/history</b> to get your 5 last actions\n" +
                              "<b>/fact</b> to get the top fact from cat-fact\n" +
                              "<b>/black_white</b> to transform your image into black & white\n" +
                              "<b>/corona_stat</b> to see 5 top provinces by new coronavirus cases",
                              parse_mode=telegram.ParseMode.HTML)


@handle_command
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def save_history(update: Update):
    with open(f"{update.message.chat.id}.json", mode="w", encoding="utf-8") as handle:  # opening file named user ID
        json.dump(USERS_ACTION, handle, ensure_ascii=False, indent=2)  # uploading actions to the file


def load_history(update: Update):
    global USERS_ACTION
    if os.stat(f"{update.message.chat.id}.json").st_size == 0:
        return
    with open(f"{update.message.chat.id}.json", mode="r", encoding="utf-8") as handle:  # opening file named user ID
        USERS_ACTION = json.load(handle)  # getting the user actions from file


@handle_command
def history(update: Update, context: CallbackContext):
    """Display 5 latest actions when the command /history is issued."""
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
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
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
        ["/black_white"]
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Choose filter",
                     reply_markup=reply_markup)


def handle_image(func):
    """Decorator for image_handler
        This function uploading image for user and calling image handler method"""

    def inner(*args, **kwargs):
        bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)
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


@handle_command
def corona_stat(update: Update, context: CallbackContext):
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    response = requests.get(
        'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports')
    soup = BeautifulSoup(response.content, 'lxml')  # Use library bs4
    last_df = get_data_frame(soup.find_all('tr', {'class': 'js-navigation-item'})[-2]).dropna()  # Get last csv
    previous_df = get_data_frame(soup.find_all('tr', {'class': 'js-navigation-item'})[-3]).dropna()# Get previous csv
    previous_df = previous_df.sort_values(by=['Province/State'])
    previous_df = previous_df.drop(['Country/Region', 'Last Update', 'Deaths', 'Recovered'], axis=1)
    last_df = last_df.drop(['Country/Region', 'Last Update', 'Deaths', 'Recovered'], axis=1)
    last_df = last_df.sort_values(by=['Province/State'])
    result = last_df.set_index('Province/State').subtract(previous_df.set_index('Province/State'))
    result = result.loc[(result['Confirmed'] > 0)]
    for province in result.sort_values(by=['Confirmed']).dropna().index[:-6:-1]:
        update.message.reply_text(f"{province}")
    maps = folium.Map(location=[43.01093752182322, 11.903098859375019], zoom_start=2.4, tiles='Stamen Terrain')
    update.message.reply_text("Your map are processing.Please, wait")
    for i in result.index.dropna():
        try:

            location = geolocator.geocode(i)
            folium.Marker(location=[location.latitude, location.longitude],
                          popup=f"{i} new confirmed: {result['Confirmed'][i]}",
                          icon=folium.Icon(color='red', icon='info-sign')).add_to(maps)
        except:
            maps.save('map.html')
    bot.send_document(chat_id=update.message.chat_id, document=open("map.html", mode='rb'))


def get_data_frame(last_csv_url):
    response = requests.get("https://github.com/" + last_csv_url.find('a').get('href'))  # Open github page with csv
    csv_html = BeautifulSoup(response.content, 'lxml')
    csv_url = (csv_html.find('a', {'class': 'btn btn-sm BtnGroup-item'})).get('href')
    return pd.read_csv("https://github.com/" + csv_url)  # Open our csv file with pandas


def main():
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('corona_stat', corona_stat))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))
    updater.dispatcher.add_handler(CommandHandler('black_white', handle_img_blk_wht))
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
