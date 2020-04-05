import json
import requests

from telegram import Update, ParseMode, Bot, ChatAction, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from bs4 import BeautifulSoup
from inline_handle import InlineKeyboardFactory


from setup import TOKEN, PROXY
from auxiliary_functions import handle_command, load_history, get_data_frame, get_corona_map, handle_image
from image_handler import ImageHandler


bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


@handle_command
def command_start(update: Update,  context: CallbackContext):
    """Send a message when the command /start is issued."""
    try:
        load_history(update)  # if file exists, load history (update for getting user ID)
    except FileNotFoundError:
        open(f"user_history/{update.message.chat.id}.json", "w+")  # if file doesn't exist, create it for a new user
    update.message.reply_text(f'Hi, {update.effective_user.first_name}!')
    update.message.reply_text('Please, type <b>/help</b> to see the list of commands.',
                              parse_mode=ParseMode.HTML)


@handle_command
def command_chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Welcome! You're using the 11'th team bot.")
    update.message.reply_text("Type:\n<b>/start</b> to start the bot\n" +
                              "<b>/help</b> to get list of commands\n" +
                              "<b>/history</b> to get your 5 last actions\n" +
                              "<b>/fact</b> to get the top fact from cat-fact\n" +
                              "<b>/black_white</b> to transform your image into black & white\n" +
                              "<b>/corona_stat</b> to see 5 top provinces by new coronavirus cases",
                              "<b>/news</b> to see fresh news about COVID-19",

                              parse_mode=ParseMode.HTML)


@handle_command
def command_echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def command_history(update: Update, context: CallbackContext):
    """Display 5 latest actions when the command /history is issued."""
    update.message.reply_text("Last 5 actions:")
    with open(f"user_history/{update.message.chat.id}.json", "r") as handle:
        data = json.load(handle)
        output = ""
        for action in data:
            for key, value in action.items():
                output += f"{key}: {value}\n"
            output += "\n"
        update.message.reply_text(output)


@handle_command
def command_fact(update: Update, context: CallbackContext):
    """This method is processing the most popular fact and sending to user"""
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    fact = requests.get("https://cat-fact.herokuapp.com/facts").json()["all"][0]
    quote = f"<i>{fact['text']}</i>"
    author = f"<b>Author: {fact['user']['name']['first']} {fact['user']['name']['last']}</b>"
    update.message.reply_text("Well, time for a good quote...")
    update.message.reply_text(f'«{quote}»\n\t                     一 {author:}', parse_mode=ParseMode.HTML)


@handle_command
def command_corona_stat(update: Update, context: CallbackContext):
    """This method is processing statistic's corona virus"""
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    response = requests.get(
        'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports')
    if response.status_code == 200:  # if the website is up, let's backup data
        with open('corona_information/corona_stat.html', "wb+") as handle:
            handle.write(response.content)
    with open('corona_information/corona_stat.html', "r") as handle:
        soup = BeautifulSoup(handle.read(), 'lxml')  # Use library bs4
    update.message.reply_text('Top 5 provinces by new infected:')
    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    last_df = get_data_frame(soup.find_all('tr', {'class': 'js-navigation-item'})[-2]).dropna()  # Get last csv
    prev_df = get_data_frame(soup.find_all('tr', {'class': 'js-navigation-item'})[-3]).dropna()  # Get previous csv
    last_df = last_df.sort_values(by=['Province_State']).reset_index(drop=True)  # Reset all indexes
    prev_df = prev_df.append(last_df[~last_df['Province_State'].isin(prev_df['Province_State'])])
    prev_df = prev_df.sort_values(by=['Province_State']).reset_index(drop=True)
    last_df['Confirmed'] = last_df['Confirmed'] - prev_df['Confirmed']  # Get count confirmed
    last_df.loc[last_df['Confirmed'] < 0] *= -1  # If new entry, it'll be less than zero, 'cause we need to change it
    last_df = last_df[last_df['Confirmed'] > 0]
    last_df = last_df.sort_values(by=['Confirmed'], ascending=False)
    place = 1
    output = ''
    for i in last_df.index[:5]:
        if last_df['Province_State'][i] != '':
            output += f"<b>{place}</b> {last_df['Combined_Key'][i]} - {last_df['Confirmed'][i]}\n"
        place += 1
    bot.send_message(chat_id=update.effective_message.chat_id, text=output,
                     reply_markup=InlineKeyboardFactory.get_inline_coronavirus_keyboard(),
                     parse_mode=ParseMode.HTML)

    update.message.reply_text("Your map is processing. Please, wait...")
    get_corona_map(data_frame=last_df)  # Get map with sick
    bot.send_document(chat_id=update.message.chat_id,  # Send to user map with sick
                      document=open("corona_information/map.html", mode='rb'))


@handle_command
def command_get_news(update: Update, context: CallbackContext):  # You can get fresh news from Yandex
    bot.send_message(chat_id=update.effective_message.chat_id,
                     text='Choose news',
                     reply_markup=InlineKeyboardFactory.get_inline_news_keyboard())


@handle_command
def command_get_image(update: Update, context: CallbackContext):
    """This method getting an image and give choice to user
            what to do with image"""
    file = update.message.photo[-1].file_id
    image = bot.get_file(file)  # Download user's image from telegram chat
    image.download('initial_user_images/initial.jpg')  # Save image
    custom_keyboard = [
        ["/black_white"],
        ["/contrast"]
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)  # Send keyboard to user
    bot.send_message(chat_id=update.message.chat_id,
                     text="Choose filter",
                     reply_markup=reply_markup)


@handle_image
@handle_command
def command_get_white_black_img(update: Update, context: CallbackContext):
    """This function is processing image by the black_white filter"""
    img = ImageHandler()
    img.get_black_white_img()

    reply_markup = ReplyKeyboardRemove()  # Remove keyboard
    bot.send_message(chat_id=update.message.chat_id,
                     text="Upload new image",
                     reply_markup=reply_markup)


@handle_command
def command_handle_contrast(update: Update, context: CallbackContext):
    """This image is processing by the contrast filter"""
    bot.send_photo(chat_id=update.effective_message.chat_id,
                   photo=open('initial_user_images/initial.jpg', mode='rb'), caption='Contrast',
                   reply_markup=InlineKeyboardFactory.get_inline_contrast_keyboard())

