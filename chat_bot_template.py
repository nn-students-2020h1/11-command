#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import telegram_commands as tg

from telegram import Update, Bot
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater, CallbackQueryHandler
from inline_handle import InlineCallback
from setup import TOKEN, PROXY

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

bot = Bot(
    token=TOKEN,
    #base_url=PROXY,  # delete it if connection via VPN
)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', tg.command_start))
    updater.dispatcher.add_handler(CommandHandler('help', tg.command_chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', tg.command_history))
    updater.dispatcher.add_handler(CommandHandler('corona_stat', tg.command_corona_stat))
    updater.dispatcher.add_handler(CommandHandler('fact', tg.command_fact))
    updater.dispatcher.add_handler(CommandHandler('black_white', tg.command_get_white_black_img))
    updater.dispatcher.add_handler(CommandHandler('contrast', tg.command_handle_contrast))
    updater.dispatcher.add_handler(CommandHandler('news', tg.command_get_news))
    updater.dispatcher.add_handler(CommandHandler('infected', tg.command_get_probability))
    updater.dispatcher.add_handler(CommandHandler('recommendation', tg.command_recommendation))
    updater.dispatcher.add_handler(CommandHandler('stat', tg.command_get_stat_in_region))

    updater.dispatcher.add_handler(MessageHandler(Filters.photo, tg.command_get_image))
    
    # location handler
    updater.dispatcher.add_handler(MessageHandler(Filters.location, tg.get_location))

    # inline handler
    updater.dispatcher.add_handler(CallbackQueryHandler(callback=InlineCallback.handle_keyboard_callback))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, tg.command_echo))

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
