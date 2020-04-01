import image_handler as img_h
import requests
import csv
import telegram

from bs4 import BeautifulSoup
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from selenium import webdriver
from setup import PROXY, TOKEN
from webdriver_manager.chrome import ChromeDriverManager

"""Buttons' identifiers for keyboard callback data"""
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


class InlineKeyboardFactory:  # provides all inline keyboards
    @staticmethod
    def get_inline_contrast_keyboard():  # keyboard for image contrast level
        """Get custom inline keyboard for modifying contrast of an image"""
        keyboard = [
            [
                InlineKeyboardButton("+0.1", callback_data=CALLBACK_BUTTON_01),  # increases contrast by 0.1
                InlineKeyboardButton("+0.5", callback_data=CALLBACK_BUTTON_05)  # increases contrast by 0.5
            ],
            [
                InlineKeyboardButton("-0.1", callback_data=CALLBACK_BUTTON_m01),  # decreases contrast by 0.1
                InlineKeyboardButton("-0.5", callback_data=CALLBACK_BUTTON_m05)  # decreases contrast by 0.5
            ],
            [
                InlineKeyboardButton("PERFECT!", callback_data=CALLBACK_BUTTON_FIN)  # finishes the editing of contrast
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_inline_coronavirus_keyboard():  # keyboard for /corona_stat
        """Get custom inline keyboard for coronavirus stats"""
        keyboard = [
            [
                InlineKeyboardButton("Russian stats", callback_data=CALLBACK_BUTTON_COVID19_RU)  # Get Russian stats
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


class InlineCallback:  # Processes the events on inline keyboards' buttons
    @staticmethod
    def handle_keyboard_callback(update: Update, context: CallbackContext):  # Gets callback_data from the pushed button
        query = update.callback_query  # Gets query from callback
        data = query.data  # callback_data of pushed button
        chat_id = update.effective_message.chat_id  # chat id for sending messages

        if data == CALLBACK_BUTTON_01:
            img_h.get_contrast_img(0.1, 'initial_user_images/initial.jpg',
                                   'initial_user_images/initial.jpg')  # replace the existing image with an enhanced one
            temp_message = bot.send_photo(chat_id=chat_id, photo=open('initial_user_images/initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboardFactory.get_inline_contrast_keyboard())
            bot.delete_message(chat_id, temp_message.message_id - 1)  # deletes previous message with an old image

        elif data == CALLBACK_BUTTON_05:
            img_h.get_contrast_img(0.5, 'initial_user_images/initial.jpg', 'initial_user_images/initial.jpg')  # replace the existing image with an enhanced one
            temp_message = bot.send_photo(chat_id=chat_id, photo=open('initial_user_images/initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboardFactory.get_inline_contrast_keyboard())
            bot.delete_message(chat_id, temp_message.message_id - 1)  # deletes previous message with an old image
        elif data == CALLBACK_BUTTON_m01:
            img_h.get_contrast_img(-0.1, 'initial_user_images/initial.jpg',
                                   'initial_user_images/initial.jpg')  # replace existing image with an enhanced one

            temp_message = bot.send_photo(chat_id=chat_id,
                                          photo=open('initial_user_images/initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboardFactory.get_inline_contrast_keyboard())

            bot.delete_message(chat_id, temp_message.message_id - 1)  # deletes previous message with an old image

        elif data == CALLBACK_BUTTON_m05:
            img_h.get_contrast_img(-0.5, 'initial_user_images/initial.jpg',
                                   'initial_user_images/initial.jpg')  # replace existing image with an enhanced one

            temp_message = bot.send_photo(chat_id=chat_id,
                                          photo=open('initial_user_images/initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboardFactory.get_inline_contrast_keyboard())
            bot.delete_message(chat_id, temp_message.message_id - 1)  # deletes previous message with an old image

        elif data == CALLBACK_BUTTON_FIN:
            img_h.get_contrast_img(1.0, 'initial_user_images/initial.jpg',
                                   'result_user_images/res.jpg')  # get final result after editing
            final_message = bot.send_photo(chat_id=chat_id,
                                           photo=open("result_user_images/res.jpg", mode='rb'))
            bot.delete_message(chat_id, final_message.message_id - 1)  # deletes previous message with an old image

            reply_markup = ReplyKeyboardRemove()  # Remove keyboard
            bot.send_message(chat_id=chat_id,
                             text='Upload new image',
                             reply_markup=reply_markup)

        elif data == CALLBACK_BUTTON_COVID19_RU:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            # installs the web driver to run JS-tables on the website

            driver.get('https://virus-zone.ru/coronavirus-v-rossii/')
            # runs the page with covid-19 data for Russia

            table = driver.find_element_by_xpath('//div[3]/div[4]/div/table')
            # find the JS-generated table with statistics on covid-19 divided by regions

            table_html = table.get_attribute('innerHTML')
            # get the html-version of JS-generated table for parsing it

            table_html = BeautifulSoup(table_html, 'html.parser')  # format it with BeautifulSoup

            headings = []  # USELESS IN CODE, NEEDED JUST FOR BETTER UNDERSTANDING: headings of a table
            for table_row in table_html.findAll('thead'):  # find html-tag for heading of a table
                columns = table_row.findAll('th')  # find all components of an html-heading by their tag <th> </th>
                heading = []  # stores single heading
                for column in columns:  # for each column's heading:
                    heading.append(column.text.strip())  # add heading without whitespaces (raw data provides heading
                    # with a number of useless whitespaces, thus we need to get only letters)
                headings.append(heading)  # add formatted heading

            output_rows = []  # ALL rows of a table
            for table_row in table_html.findAll('tr'):  # find html-tag for row of a table
                columns = table_row.findAll('td')  # find each cell of a row
                output_row = []  # SINGLE row
                for column in columns:  # for each cell:
                    output_row.append(column.text.strip())  # add cell to the row without whitespaces
                output_rows.append(output_row)  # add formatted row and go to the next one

            with open('covid_ru.csv', 'w', newline='') as csvfile:  # open .csv file for storing our covid-19 RU data
                writer = csv.writer(csvfile)  # csv writer for this file
                writer.writerows(headings)  # firstly, add headings
                writer.writerows(output_rows)  # then add all rows from table

            with open('covid_ru.csv', 'r') as handle:  # open .csv file to get our covid-19 RU data
                reader = handle.readlines()[2:7]  # ignore heading and 1 empty line
                place = 0  # counter for the top-5
                for row in reader:
                    place += 1
                    if any(row):  # if the line is not empty
                        content = row.split(',')  # split the row by ',' symbol
                        bot.send_message(chat_id=chat_id, text=f'<b>{place}.</b> '
                                         f'{content[0]}: {content[1]} cases\n',
                                         parse_mode=telegram.ParseMode.HTML)  # content[0] - city name,
                                                                              # content[1] - number of cases
