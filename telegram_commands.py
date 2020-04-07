import json
import requests
import csv
import lxml.html as lh

from telegram import Update, ParseMode, Bot, ChatAction, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import CallbackContext
from inline_handle import InlineKeyboardFactory
from bs4 import BeautifulSoup
from setup import TOKEN, PROXY
from auxiliary_functions import handle_command, load_history, get_data_frame, get_corona_map, handle_image
from image_handler import ImageHandler
from countryinfo import CountryInfo
from googletrans import Translator
from geopy.geocoders import Nominatim
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from lxml import html

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


@handle_command
def command_start(update: Update, context: CallbackContext):
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
                              "<b>/corona_stat</b> to see 5 top provinces by new coronavirus cases\n" +
                              "<b>/news</b> to see fresh news about COVID-19\n" +
                              "<b>/infected</b> to get the probability of you getting COVID-19\n" +
                              "<b>/recommendation</b> to get the recommendation about COVID-19\n",
                              parse_mode=ParseMode.HTML
                              )


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
                     reply_markup=InlineKeyboardFactory.create_inline_keyboard("coronavirus"),
                     parse_mode=ParseMode.HTML)

    update.message.reply_text("Your map is processing. Please, wait...")
    get_corona_map(data_frame=last_df)  # Get map with sick
    bot.send_document(chat_id=update.message.chat_id,  # Send to user map with sick
                      document=open("corona_information/map.html", mode='rb'))


@handle_command
def command_get_news(update: Update, context: CallbackContext):  # You can get fresh news from Yandex
    bot.send_message(chat_id=update.effective_message.chat_id,
                     text='Choose news',
                     reply_markup=InlineKeyboardFactory.create_inline_keyboard("news"))


@handle_command
def command_recommendation(update: Update, context: CallbackContext):
    """This method send some recommendation about prevention from COVID-19"""
    import random
    recommendation_list = ['Wash your hands frequently',
                           'Maintain social distancing',
                           'Avoid touching eyes, nose and mouth',
                           'Practice respiratory hygiene',
                           'If you have fever, cough and difficulty breathing, seek medical care early',
                           'Follow the news on latest coronavirus updates',
                           'Do not spread rumors',
                           'Check in regularly especially with those affected',
                           'Disinfect your mobile phone after going out',
                           'Do not drink alcohol - this contribute weaken the immune system']
    update.message.reply_text(random.choice(recommendation_list))


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
                   reply_markup=InlineKeyboardFactory.create_inline_keyboard("contrast"))


@handle_command
def command_get_probability(update: Update, context: CallbackContext):
    """Returns the probability of being infected based on user answers"""
    location_button = KeyboardButton('Send my location', request_location=True)
    keyboard = ReplyKeyboardMarkup([[location_button]])
    bot.send_message(chat_id=update.message.chat_id, text="Firstly, let's figure out where are you from...",
                     reply_markup=keyboard)


def get_location(update: Update, context: CallbackContext):
    """Get user's location"""
    location = f"{update.message.location.latitude}, {update.message.location.longitude}"
    with open(f"personal_{update.message.chat.id}.json", 'w+') as handle:
        json.dump({"location": location}, handle, ensure_ascii=False, indent=2)
    bot.send_message(chat_id=update.message.chat_id, text="Got your location!", reply_markup=ReplyKeyboardRemove())
    bot.send_message(chat_id=update.message.chat_id, text="Next, do you stay at home during quarantine?",
                     reply_markup=InlineKeyboardFactory.create_inline_keyboard("stayhome"))


def calc_probability(chat_id):
    personal = []
    with open(f"personal_{chat_id}.json", 'r') as handle:
        personal = json.load(handle)

    geolocator = Nominatim(user_agent="tg_bot")
    location = geolocator.reverse(personal["location"], language='ru')
    country = location.address.split(', ')[-1]

    chance = 1.0

    if personal["at_home"]:
        chance *= 0.5
    else:
        chance *= 10

    if personal["blood"] == 1:
        chance *= 0.7
    elif personal["blood"] == 2:
        chance *= 1.2

    # fix for US due to wrong geopy formatting
    if country == "Соединённые Штаты Америки":
        country = "США"

    try:
        driver = webdriver.Chrome(ChromeDriverManager().install())
    except ValueError:
        driver = "ВСТАВЬТЕ_ПУТЬ_К_chromedriver.exe, например C:/Python36/chromedriver.exe"
    # installs the web driver to run JS-tables on the website

    driver.get('https://virus-zone.ru/coronavirus-v-mire/')
    # runs the page with covid-19 data for World

    table = driver.find_element_by_xpath('/html/body/div[3]/div[6]/div/table')
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

    with open('corona_information/covid_data.csv', 'w', newline='') as csvfile:  # open .csv file for storing our covid-19 RU data
        writer = csv.writer(csvfile)  # csv writer for this file
        writer.writerows(headings)  # firstly, add headings
        writer.writerows(output_rows)  # then add all rows from table

    with open('corona_information/covid_data.csv', 'r') as handle:  # open .csv file to get our covid-19 RU data
        reader = handle.readlines()[2::]  # ignore heading and 1 empty line
        for row in reader:
            if any(row):  # if the line is not empty
                data_country = row.split(',')[0]  # split the row by ',' symbol, select first (Country)
                if data_country == country:
                    translator = Translator()  # to get country name in English
                    infected = row.split(',')[1].split(' ')[0]  # without last split data would be like 6453 (+678),
                    # so we don't need (+678)
                    population = CountryInfo(f"{translator.translate(country, dest='en', src='ru').text}").population()
                    # translate country name into English, then get its population using CountryInfo library
                    chance *= (int(infected) * 10) / int(population)

    return format(chance, '.8f')
