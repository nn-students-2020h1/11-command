from uno.deck import Deck
from uno.player import Player
from uno.card import COLORS, SPECIAL_CARDS
import random
import os

from telegram import Bot
from PIL import Image
from setup import TOKEN, PROXY

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)

DRAW_TWO = 'draw_2'
DRAW_FOUR = 'draw_4'
CHOOSE_COLOR = 'choose_color'
SKIP = 'skip'


class Game:
    current_player = None
    choosing_color = False
    started = False
    draw_counter = 0

    def __init__(self):
        self.players = list()
        self.last_card = None
        self.round = 1
        self.temp_messages = []

        while not self.last_card or self.last_card.special:
            self.deck = Deck()
            self.last_card = self.deck.get_card()

    def add_player(self, player: Player):
        if self.players.__len__() == 0:
            self.players.append(player)
            self.current_player = player
        else:
            self.players[0].prev = player
            self.players[self.players.__len__() - 1].next = player
            player.prev = self.players[self.players.__len__() - 1]
            player.next = self.players[0]
            self.players.append(player)

    def next_turn(self):
        if self.draw_counter != 0:
            self.current_player.next.draw()
        self.current_player = self.current_player.next
        if not self.current_player.is_human:
            self.current_player.play()
        else:
            from telegram_commands import uno_play_msg
            uno_play_msg(chat_id=self.current_player.chat_id, game=self.current_player.game)
        self.round += 1

    def skip_next(self):
        if self.draw_counter != 0:
            self.current_player.next.draw()
        self.current_player = self.current_player.next.next
        if not self.current_player.is_human:
            self.current_player.play()
        else:
            from telegram_commands import uno_play_msg
            uno_play_msg(chat_id=self.current_player.chat_id, game=self.current_player.game)
        self.round += 1

    def play_card(self, card):
        self.deck.beaten(self.last_card)
        self.last_card = card
        self.get_board(f"{self.current_player.name} played {card.color} {card.value} {card.special}!")

        if card.value == DRAW_TWO:
            self.draw_counter += 2
            self.skip_next()
            return None
        elif card.value == SKIP:
            self.skip_next()
            return None
        elif card.special == CHOOSE_COLOR:  # ADD INLINE COLOR KEYBOARD
            print("CHOOSING COLOR!")
            self.temp_messages.append(bot.send_message(chat_id=self.current_player.chat_id, text="CHOOSING COLOR!"))
            if not self.current_player.is_human:
                self.choose_color(random.choice(COLORS))
            else:
                from inline_handle import InlineKeyboardFactory
                self.temp_messages.append(bot.send_message(chat_id=self.current_player.chat_id, text="Choose color:",
                                                           reply_markup=InlineKeyboardFactory.get_inline_uno_choose_color()))  # noqa E501
            return None
        elif card.special == DRAW_FOUR:
            self.draw_counter += 4
            if not self.current_player.is_human:
                self.choose_color(random.choice(COLORS))
            else:
                from inline_handle import InlineKeyboardFactory
                bot.send_message(chat_id=self.current_player.chat_id, text="Choose color:",
                                 reply_markup=InlineKeyboardFactory.get_inline_uno_choose_color())
            print(f"Chosen color {self.last_card.color}")
            return None
        elif card.special not in SPECIAL_CARDS:
            self.next_turn()
            return None
        self.next_turn()
        return None

    def choose_color(self, color: COLORS):
        self.last_card.color = color
        print(f"Chosen color {self.last_card.color}")
        self.temp_messages.append(bot.send_message(chat_id=self.current_player.chat_id,
                                                   text=f"Chosen color {self.last_card.color}"))
        self.next_turn()

    def get_board(self, message: str = None):
        if self.round == 1:
            try:
                os.remove("uno/images/playing_bg.png")
                os.remove("uno/images/playing_bg_tmp.jpg")
            except FileNotFoundError:
                pass
        try:
            raw_bg = Image.open("uno/images/playing_bg.png")
        except FileNotFoundError:
            raw_bg = Image.open("uno/images/background.png")
        bg = Image.new('RGBA', (raw_bg.width, raw_bg.height))
        bg.paste(raw_bg, (0, 0))
        angle = random.randint(-15, 15)
        bg.paste(self.last_card.get_img().rotate(angle, expand=1.0),
                 (raw_bg.width // 2 - 200 - random.randint(-50, 50),
                  raw_bg.height // 2 - 200 - random.randint(-30, 30)),
                 self.last_card.get_img().rotate(angle, expand=1.0))
        bg.save("uno/images/playing_bg.png")
        temp = Image.open("uno/images/playing_bg.png")
        tmp_c = temp.convert('RGB')
        tmp_c.save("uno/images/playing_bg_tmp.jpg")
        self.temp_messages.append(bot.send_photo(chat_id=self.current_player.chat_id,
                                                 photo=open("uno/images/playing_bg_tmp.jpg", mode='rb'),
                                                 caption=message))

    @staticmethod
    def choose_color_static(current_game, color: COLORS) -> None:
        current_game.last_card.color = color
        current_game.temp_messages.append(bot.send_message(chat_id=current_game.current_player.chat_id,
                                                           text=f"Chosen color {current_game.last_card.color}"))
        current_game.next_turn()
