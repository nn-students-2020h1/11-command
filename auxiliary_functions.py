import json
import time
import os
import requests
import pandas as pd
import folium
from bs4 import BeautifulSoup
from telegram import Update, ChatAction, Bot
from setup import TOKEN


bot = Bot(
    token=TOKEN  # delete it if connection via VPN
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
            return
    except FileNotFoundError:
        return
    with open(f"{update.message.chat.id}.json", mode="r", encoding="utf-8") as handle:  # opening file named user ID
        USERS_ACTION = json.load(handle)  # getting the user actions from file


def save_history(update: Update):
    """Save user's history"""
    try:
        with open(f"user_history/{update.message.chat.id}.json",
                  mode="w", encoding="utf-8") as handle:  # opening file named user ID
            json.dump(USERS_ACTION, handle, ensure_ascii=False, indent=2)  # uploading actions to the file
    except FileNotFoundError:
        with open(f"user_history/{update.message.chat.id}.json",
                  mode="w+") as handle:  # opening file named user ID
            json.dump(USERS_ACTION, handle, ensure_ascii=False, indent=2)  # uploading actions to the file


def get_data_frame(last_csv_url):
    response = requests.get("https://github.com/" + last_csv_url.find('a').get('href'))  # Open github page with csv
    csv_html = BeautifulSoup(response.content, 'lxml')
    csv_url = (csv_html.find('a', {'class': 'btn btn-sm BtnGroup-item'})).get('href')
    return pd.read_csv("https://github.com/" + csv_url)  # Open our csv file with pandas


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


