import image_handler as img_h
import requests
import csv
import telegram

from bs4 import BeautifulSoup
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from selenium import webdriver
from setup import PROXY, TOKEN
from webdriver_manager.chrome import ChromeDriverManager

CALLBACK_BUTTON_01 = "callback_increase_01"
CALLBACK_BUTTON_05 = "callback_increase_05"
CALLBACK_BUTTON_m01 = "callback_decrease_01"
CALLBACK_BUTTON_m05 = "callback_decrease_05"
CALLBACK_BUTTON_FIN = "callback_finish"

CALLBACK_BUTTON_COVID19_RU = "callback_covid19_ru"

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


class InlineKeyboard():
    @staticmethod
    def get_inline_contrast_keyboard():
        """Get custom inline keyboard for modifying contrast of an image"""
        keyboard = [
            [
                InlineKeyboardButton("+0.1", callback_data=CALLBACK_BUTTON_01),
                InlineKeyboardButton("+0.5", callback_data=CALLBACK_BUTTON_05)
            ],
            [
                InlineKeyboardButton("-0.1", callback_data=CALLBACK_BUTTON_m01),
                InlineKeyboardButton("-0.5", callback_data=CALLBACK_BUTTON_m05)
            ],
            [
                InlineKeyboardButton("PERFECT!", callback_data=CALLBACK_BUTTON_FIN)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_inline_coronavirus_keyboard():
        """Get custom inline keyboard for coronavirus stats"""
        keyboard = [
            [
                InlineKeyboardButton("Russia stats", callback_data=CALLBACK_BUTTON_COVID19_RU)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


class InlineCallback():
    @staticmethod
    def handle_keyboard_callback(update: Update, context: CallbackContext):
        query = update.callback_query
        data = query.data
        chat_id = update.effective_message.chat_id

        if data == CALLBACK_BUTTON_01:
            img_h.get_contrast_img(0.1, 'initial.jpg', 'initial.jpg')
            temp_message = bot.send_photo(chat_id=chat_id, photo=open('initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboard.get_inline_contrast_keyboard())
            bot.delete_message(chat_id, temp_message.message_id - 1)

        elif data == CALLBACK_BUTTON_05:
            img_h.get_contrast_img(0.5, 'initial.jpg', 'initial.jpg')
            temp_message = bot.send_photo(chat_id=chat_id, photo=open('initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboard.get_inline_contrast_keyboard())
            bot.delete_message(chat_id, temp_message.message_id - 1)
        elif data == CALLBACK_BUTTON_m01:
            img_h.get_contrast_img(-0.1, 'initial.jpg', 'initial.jpg')
            temp_message = bot.send_photo(chat_id=chat_id, photo=open('initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboard.get_inline_contrast_keyboard())
            bot.delete_message(chat_id, temp_message.message_id - 1)
        elif data == CALLBACK_BUTTON_m05:
            img_h.get_contrast_img(-0.5, 'initial.jpg', 'initial.jpg')
            temp_message = bot.send_photo(chat_id=chat_id, photo=open('initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboard.get_inline_contrast_keyboard())
            bot.delete_message(chat_id, temp_message.message_id - 1)
        elif data == CALLBACK_BUTTON_FIN:
            img_h.get_contrast_img(1.0, 'initial.jpg', 'res.jpg')
            final_message = bot.send_photo(chat_id=chat_id, photo=open("res.jpg", mode='rb'))
            bot.delete_message(chat_id, final_message.message_id - 1)

        elif data == CALLBACK_BUTTON_COVID19_RU:
            html = requests.get('https://virus-zone.ru/coronavirus-v-rossii/').text
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get('https://virus-zone.ru/coronavirus-v-rossii/')
            table = driver.find_element_by_xpath('//div[3]/div[4]/div/table')
            table_html = table.get_attribute('innerHTML')
            with open('data.html', 'w+') as handle:
                handle.write(table_html)
            table_html = BeautifulSoup(table_html, 'html.parser')

            headings = []
            for table_row in table_html.findAll('thead'):
                columns = table_row.findAll('th')
                heading = []
                for column in columns:
                    heading.append(column.text.strip())
                headings.append(heading)

            output_rows = []
            for table_row in table_html.findAll('tr'):
                columns = table_row.findAll('td')
                output_row = []
                for column in columns:
                    output_row.append(column.text.strip())
                output_rows.append(output_row)

            with open('covid_ru.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(headings)
                writer.writerows(output_rows)

            with open('covid_ru.csv', 'r') as handle:
                reader = handle.readlines()[2:7]
                place = 0
                for row in reader:
                    if place == 0:
                        place += 1
                        pass
                    if any(row):
                        content = row.split(',')
                        bot.send_message(chat_id=chat_id, text=f'<b>{place}.</b> {content[0]}: {content[1]} cases\n',
                                     parse_mode=telegram.ParseMode.HTML)
                        place += 1
                    if place == 6:
                        break
                        
