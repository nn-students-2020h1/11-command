import json
import requests
import csv
import inline_handle

from telegram import Update, ParseMode, Bot, ChatAction, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import CallbackContext
from bs4 import BeautifulSoup
from setup import TOKEN, PROXY
from auxiliary_functions import handle_command, handle_image, get_list_actions, handle_message
from image_handler import ImageHandler
from countryinfo import CountryInfo
from googletrans import Translator
from geopy.geocoders import Nominatim
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from covid_stat import CovidRegionStat, CovidWorldStat
from uno.game import Game

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)

GAME = None
CHAT_ID = None


@handle_command
def command_start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    try:
        #  load_history(update)  # if file exists, load history (update for getting user ID)
        pass
    except FileNotFoundError:
        open(f"user_history/{update.message.chat.id}.json", "w+")  # if file doesn't exist, create it for a new user
    update.message.reply_text(f'Hi, {update.effective_user.first_name}!')
    update.message.reply_text('Please, type <b>/help</b> to see the list of commands.',
                              parse_mode=ParseMode.HTML)
    return update.effective_user.first_name


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
                              "<b>/recommendation</b> to get the recommendation about COVID-19\n" +
                              "<b>/stat + your region</b> to get the covid_19 plot your region\n" +
                              "<b>/uno</b> to play UNO game\n",
                              parse_mode=ParseMode.HTML
                              )
    return "success"


@handle_command
def command_echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    response = handle_message(update.message.text)
    update.message.reply_text(response, parse_mode=ParseMode.HTML)
    return response


def get_quote(url: str):
    try:
        fact = requests.get(url=url)
        if fact is None or not fact.ok:
            raise ConnectionError
        else:
            try:
                fact = fact.json()["all"][0]
                quote = f"<i>{fact['text']}</i>"
                author = f"<b>Author: {fact['user']['name']['first']} {fact['user']['name']['last']}</b>"
            except KeyError:
                return ["You're awesome.", "Our KeyError"]
        return [quote, author]
    except ConnectionError:
        return ["You're awesome.", "Our ConnectionError"]


def command_history(update: Update, context: CallbackContext):
    """Display 5 latest actions when the command /history is issued."""
    update.message.reply_text("Last 5 actions:")
    actions = get_list_actions(str(update.message.chat_id))
    output = ''
    for action in actions[:-6:-1]:
        output += str(f"<b>function:</b> {action[1]}, <b>text</b>: {action[2]}, <b>time</b>: {action[3]}\n")

    update.message.reply_text(output, parse_mode=ParseMode.HTML)
    return output


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
    user_message = update.message['text']
    user_date = user_message.replace('/corona_stat', '').strip()

    user_message = update.message['text']
    user_date = user_message.replace('/corona_stat', '').strip()

    top_province = CovidWorldStat()

    top_province.set_date(days_ago=1)
    if user_date:
        try:
            top_province.set_user_date(user_date)
            top_province.set_data_frame()

        except Exception as ex:
            bot.send_message(chat_id=update.effective_message.chat_id,
                             text=str(ex))
            return None

    top_covid_places = top_province.get_difference_disease(top=5)
    top_places_message = ''
    for place in top_covid_places:
        top_places_message += place
    bot.send_message(chat_id=update.effective_message.chat_id, text=top_places_message,
                     reply_markup=inline_handle.InlineKeyboardFactory.get_inline_coronavirus_keyboard(),
                     parse_mode=ParseMode.HTML)
    update.message.reply_text("Your map is processing. Please, wait...")
    bot.send_document(chat_id=update.message.chat_id,  # Send to user map with sick
                      document=open("corona_information/map.html", mode='rb'))


@handle_command
def command_get_news(update: Update, context: CallbackContext):  # You can get fresh news from Yandex
    bot.send_message(chat_id=update.effective_message.chat_id,
                     text='Choose news',
                     reply_markup=inline_handle.InlineKeyboardFactory.get_inline_news_keyboard())


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
def command_get_stat_in_region(update: Update, context: CallbackContext):
    user_message = update.message['text']
    user_request = user_message.replace('/stat', '').strip()
    covid_request = CovidRegionStat()

    if user_request in covid_request.get_list_of_regions():
        href = covid_request.get_specific_region_href(region_name=user_request)
        covid_request.get_and_save_csv_table(href_by_region=href, user_id=update.message.chat_id)
        covid_request.get_plot_region()
        bot.send_photo(chat_id=update.effective_message.chat_id,
                       photo=open(covid_request.get_path_to_plot_file(), mode='rb'))
    else:
        one_vector = covid_request.transform_into_np_vector(user_request)
        two_vector = covid_request.get_result_alphabet()
        s = covid_request.get_cosine(one_vector, two_vector)
        s = sorted(s, key=lambda x: x[1])
        output = ''
        epsilon = 0.350
        for i in s[:2]:
            if i[1] <= epsilon:
                output += str(covid_request.get_specific_region_by_index(i[0])) + '\n'

        if output == '':
            for i in covid_request.get_list_of_regions():
                output += str(i) + '\n'
        #
        update.message.reply_text(f"Maybe: \n{str(output)}")


def command_handle_contrast(update: Update, context=None):
    """This image is processing by the contrast filter"""
    try:
        bot.send_photo(chat_id=update.effective_message.chat_id,
                       photo=open('initial_user_images/initial.jpg', mode='rb'), caption='Contrast',
                       reply_markup=inline_handle.InlineKeyboardFactory.get_inline_contrast_keyboard())
    except FileNotFoundError:
        return "Initial image wasn't found."


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
                     reply_markup=inline_handle.InlineKeyboardFactory.get_inline_stayhome())


def calc_probability(chat_id):  # noqa: C901  # TODO: will fix this later
    personal = []
    with open(f"personal_{chat_id}.json", 'r') as handle:
        personal = json.load(handle)

    geolocator = Nominatim(user_agent="tg_bot")
    location = geolocator.reverse(personal["location"], language='en')
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

    table = driver.find_element_by_xpath('/html/body/div[3]/div[8]/div/table')
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

    with open('corona_information/covid_data.csv', 'w', newline='') as csvfile:
        # open .csv file for storing our covid-19 RU data
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


@handle_command
def command_uno(update: Update, context=None):
    bot.send_message(chat_id=update.message.chat_id, text="Welcome to UNO-11! Who do you want to play with?",
                     reply_markup=inline_handle.InlineKeyboardFactory.get_inline_uno_choose_player())


def uno_game_handler(update: Update, chat_id: str, players: list, game: Game):
    bot.send_message(chat_id=chat_id, text="Your opponent: Boss!")
    for player in players:
        game.add_player(player)
    game.started = True
    if game.current_player.is_human:
        uno_play_msg(chat_id=chat_id, game=game)
    else:
        game.current_player.play()
        bot.send_message(chat_id=chat_id,
                         text=f"{game.current_player.name} has {game.current_player.cards.__len__()} cards")


def uno_play_msg(chat_id: str, game: Game):
    if not game.current_player.cards.__len__() == 0:
        players = game.players
        bot.send_message(chat_id=chat_id, text=f"Your turn! Boss has {players[1].cards.__len__()} cards...")
        bot.send_message(chat_id=chat_id,
                     text=f"Play the special card or {game.last_card.color} card or value {game.last_card.value} card. Type X for draw. Your deck:")  # noqa: E501  # TODO: will fix this later
        bot.send_message(chat_id=chat_id, text=players[0].view_deck())
        bot.send_message(chat_id=chat_id, text="Choose card by index:",
                         reply_markup=game.current_player.deck_choose_keyboard())
