import image_handler as img_h

from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from setup import PROXY, TOKEN

CALLBACK_BUTTON_01 = "callback_increase_01"
CALLBACK_BUTTON_05 = "callback_increase_05"
CALLBACK_BUTTON_m01 = "callback_decrease_01"
CALLBACK_BUTTON_m05 = "callback_decrease_05"
CALLBACK_BUTTON_FIN = "callback_finish"

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
