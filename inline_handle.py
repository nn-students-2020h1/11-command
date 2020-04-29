import image_handler as img_h
import requests
import telegram
import json
import telegram_commands as tg

from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from setup import TOKEN
from covid_news import CovidNews
from lxml import html
from uno.player import Player
from uno.game import Game

"""Buttons' identifiers for keyboard callback data"""
CALLBACK_BUTTON_01 = "callback_increase_01"
CALLBACK_BUTTON_05 = "callback_increase_05"
CALLBACK_BUTTON_m01 = "callback_decrease_01"
CALLBACK_BUTTON_m05 = "callback_decrease_05"
CALLBACK_BUTTON_FIN = "callback_finish"

CALLBACK_BUTTON_COVID19_RU = "callback_covid19_ru"

CALLBACK_BUTTON_NEWS_01 = "first_news"
CALLBACK_BUTTON_NEWS_02 = "second_news"
CALLBACK_BUTTON_NEWS_03 = "third news"
CALLBACK_BUTTON_NEWS_04 = "other_news"
CALLBACK_BUTTON_NEWS_06 = "read more in source"
CALLBACK_BUTTON_NEWS_07 = "refuse to read more"

CALLBACK_BUTTON_STAYHOME = "callback_stay_home"
CALLBACK_BUTTON_NOSTAY = "callback_no_stay"
CALLBACK_BUTTON_BLOOD_I = "callback_blood_I"
CALLBACK_BUTTON_BLOOD_II = "callback_blood_II"
CALLBACK_BUTTON_BLOOD_III = "callback_blood_III"
CALLBACK_BUTTON_BLOOD_IV = "callback_blood_IV"

CALLBACK_BUTTON_UNO_BOT = "callback_uno_bot"
CALLBACK_BUTTON_UNO_DRAW_ONE = "callback_uno_draw_one"

bot = Bot(
    token=TOKEN,
)

Covid = CovidNews()


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

    @staticmethod
    def get_inline_news_keyboard():  # Get three news buttons
        Covid.shuffle_news()
        keyboard = [
            [
                InlineKeyboardButton(Covid.get_title_news(0),
                                     callback_data=CALLBACK_BUTTON_NEWS_01)
            ],
            [
                InlineKeyboardButton(Covid.get_title_news(1),
                                     callback_data=CALLBACK_BUTTON_NEWS_02)
            ],
            [
                InlineKeyboardButton(Covid.get_title_news(2),
                                     callback_data=CALLBACK_BUTTON_NEWS_03)
            ],
            [
                InlineKeyboardButton("Other",
                                     callback_data=CALLBACK_BUTTON_NEWS_04),
                InlineKeyboardButton("Close",
                                     callback_data=CALLBACK_BUTTON_NEWS_07)
            ]
        ]

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_inline_keyboard_more_information():
        keyboard = [
            [
                InlineKeyboardButton("Read more in source",
                                     callback_data=CALLBACK_BUTTON_NEWS_06),  # Get Russian stats
                InlineKeyboardButton("Other",
                                     callback_data=CALLBACK_BUTTON_NEWS_04)
            ],
            [
                InlineKeyboardButton("Close", callback_data=CALLBACK_BUTTON_NEWS_07)  # Get Russian stats
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_inline_stayhome():
        """Get custom inline keyboard for coronavirus infection probability"""
        keyboard = [
            [
                InlineKeyboardButton("YES", callback_data=CALLBACK_BUTTON_STAYHOME),
                InlineKeyboardButton("NO", callback_data=CALLBACK_BUTTON_NOSTAY)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_inline_bloodtype():
        keyboard = [
            [
                InlineKeyboardButton("I (0)", callback_data=CALLBACK_BUTTON_BLOOD_I)
            ],
            [
                InlineKeyboardButton("II (A)", callback_data=CALLBACK_BUTTON_BLOOD_II)
            ],
            [
                InlineKeyboardButton("III (B)", callback_data=CALLBACK_BUTTON_BLOOD_III)
            ],
            [
                InlineKeyboardButton("IV (AB)", callback_data=CALLBACK_BUTTON_BLOOD_IV)
            ],
            [
                InlineKeyboardButton("I don't know", callback_data=CALLBACK_BUTTON_BLOOD_I)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_inline_uno_choose_player():
        keyboard = [
            [
                InlineKeyboardButton("Boss", callback_data=CALLBACK_BUTTON_UNO_BOT)
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


class InlineCallback:  # Processes the events on inline keyboards' buttons

    @staticmethod
    def update_data(add_data: {}, file: json):
        with open(file, "r") as handle:
            data = json.load(handle)
        data.update(add_data)
        with open(file, "w") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        return file, add_data

    @staticmethod  # noqa: C901  # TODO: it works, so I don't wanna to ruin it
    def handle_keyboard_callback(update: Update, context=None):  # Gets callback_data from the pushed button
        query = update.callback_query  # Gets query from callback
        data = query.data  # callback_data of pushed button
        chat_id = update.effective_message.chat_id  # chat id for sending messages

        if data == CALLBACK_BUTTON_01:
            img_h.get_contrast_img(0.1, 'initial_user_images/initial.jpg',
                                   'initial_user_images/initial.jpg')  # replace the existing image with an enhanced one
            temp_message = bot.send_photo(chat_id=chat_id, photo=open('initial_user_images/initial.jpg', mode='rb'),
                                          reply_markup=InlineKeyboardFactory.get_inline_contrast_keyboard())
            bot.delete_message(chat_id, temp_message.message_id - 1)  # deletes previous message with an old image
            return CALLBACK_BUTTON_01

        elif data == CALLBACK_BUTTON_05:
            img_h.get_contrast_img(0.5, 'initial_user_images/initial.jpg',
                                   'initial_user_images/initial.jpg')  # replace the existing image with an enhanced one
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
            img_h.get_contrast_img(0.0, 'initial_user_images/initial.jpg',
                                   'result_user_images/res.jpg')  # get final result after editing
            final_message = bot.send_photo(chat_id=chat_id,
                                           photo=open("result_user_images/res.jpg", mode='rb'))
            bot.delete_message(chat_id, final_message.message_id - 1)  # deletes previous message with an old image

            reply_markup = ReplyKeyboardRemove()  # Remove keyboard
            bot.send_message(chat_id=chat_id,
                             text='Upload new image',
                             reply_markup=reply_markup)

        elif data == CALLBACK_BUTTON_COVID19_RU:
            page = requests.get("https://yandex.ru/maps/covid19?ll=41.775580%2C54.894027&z=3")
            tree = html.fromstring(page.content)
            rows = tree.xpath('//div[@class="covid-panel-view__item"]')
            place = 0
            for row in rows:
                region = row.xpath('//div[@class="covid-panel-view__item-name"]/text()')[place]
                cases = row.xpath('//div[@class="covid-panel-view__item-cases"]/text()')[place].replace("\xa0", "")
                place += 1
                bot.send_message(chat_id=chat_id, text=f'<b>{place}.</b> '
                                                       f'{region}: {cases} cases\n',
                                 parse_mode=telegram.ParseMode.HTML)
                if place == 5:
                    break

        elif data == CALLBACK_BUTTON_NEWS_01:

            Covid.send_message(bot=bot, chat_id=chat_id, value=0)

            bot.send_message(chat_id=update.effective_message.chat_id,
                             text="Do you want to read more?",
                             reply_markup=InlineKeyboardFactory.get_inline_keyboard_more_information())

        elif data == CALLBACK_BUTTON_NEWS_02:  # Choose second news

            Covid.send_message(bot=bot, chat_id=chat_id, value=1)

            bot.send_message(chat_id=update.effective_message.chat_id,
                             text="Do you want to read more?",
                             reply_markup=InlineKeyboardFactory.get_inline_keyboard_more_information())

        elif data == CALLBACK_BUTTON_NEWS_03:  # Choose second news

            Covid.send_message(bot=bot, chat_id=chat_id, value=2)

            bot.send_message(chat_id=update.effective_message.chat_id,
                             text="Do you want to read more?",
                             reply_markup=InlineKeyboardFactory.get_inline_keyboard_more_information())

        elif data == CALLBACK_BUTTON_NEWS_04:  # Choose other news

            InlineKeyboardFactory.get_inline_news_keyboard()
            temp = bot.send_message(chat_id=update.effective_message.chat_id,
                                    text='Choose news',
                                    reply_markup=InlineKeyboardFactory.get_inline_news_keyboard())
            bot.delete_message(chat_id, temp.message_id - 1)

        elif data == CALLBACK_BUTTON_NEWS_06:  # Choose read more about certain news

            temp = bot.send_message(chat_id=chat_id,
                                    text=Covid.get_href_news())

            bot.delete_message(chat_id, temp.message_id - 1)

        elif data == CALLBACK_BUTTON_NEWS_07:
            temp = bot.send_message(chat_id=chat_id,
                                    text="I will be waiting for you here")
            bot.delete_message(chat_id, temp.message_id - 1)

        elif data == CALLBACK_BUTTON_STAYHOME:
            InlineCallback.update_data({"at_home": True}, f"personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id, text="Perfect! Now, select your blood type...",
                             reply_markup=InlineKeyboardFactory.get_inline_bloodtype())

        elif data == CALLBACK_BUTTON_NOSTAY:
            InlineCallback.update_data({"at_home": False}, f"personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id,
                             text="I strongly recommend you to stay home! Now, select your blood type...",
                             reply_markup=InlineKeyboardFactory.get_inline_bloodtype())

        elif data == CALLBACK_BUTTON_BLOOD_I:
            InlineCallback.update_data({"blood": 1}, f"personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id,
                             text="Thanks! Now I can calculate the coronavirus pick up probability for you.")
            bot.send_message(chat_id=chat_id,
                             text=f"The probability of you getting COVID-19 is around {tg.calc_probability(chat_id)}%")

        elif data == CALLBACK_BUTTON_BLOOD_II:
            InlineCallback.update_data({"blood": 2}, f"personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id,
                             text="Thanks! Now I can calculate the coronavirus pick up probability for you.")
            bot.send_message(chat_id=chat_id,
                             text=f"The probability of you getting COVID-19 is around {tg.calc_probability(chat_id)}%")

        elif data == CALLBACK_BUTTON_BLOOD_III or data == CALLBACK_BUTTON_BLOOD_IV:
            InlineCallback.update_data({"blood": 3}, f"personal_{chat_id}.json")
            bot.send_message(chat_id=chat_id,
                             text="Thanks! Now I can calculate the coronavirus pick up probability for you.")
            bot.send_message(chat_id=chat_id,
                             text=f"The probability of you getting COVID-19 is around {tg.calc_probability(chat_id)}%")

        elif data == CALLBACK_BUTTON_UNO_BOT:
            game = Game()
            tg.GAME = game
            tg.CHAT_ID = chat_id
            tg.uno_game_handler(update=update, chat_id=chat_id, players=[Player(chat_id=chat_id,
                                                                                game=game, is_human=True, name='You'),
                                                                         Player(chat_id=chat_id,
                                                                                game=game, is_human=False,
                                                                                name='Boss')], game=game)

        elif data == CALLBACK_BUTTON_UNO_DRAW_ONE:
            tg.GAME.current_player.draw()
            tg.GAME.next_turn()

        elif data.__len__() < 3:
            if tg.GAME.current_player.cards[int(data)].value == "draw_2" or tg.GAME.current_player.cards[int(data)].value == "skip":
                tg.GAME.current_player.play(tg.GAME.current_player.cards[int(data)])
                '''if tg.GAME.current_player.is_human:
                    tg.uno_play_msg(chat_id=chat_id, game=tg.GAME)
                else:
                    tg.GAME.current_player.play()'''
            else:
                tg.GAME.current_player.play(tg.GAME.current_player.cards[int(data)])
