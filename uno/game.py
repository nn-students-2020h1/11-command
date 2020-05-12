from uno.deck import Deck
from uno.player import Player
from uno.card import COLORS, SPECIAL_CARDS
import random

from telegram import Bot
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

    def skip_next(self):
        if self.draw_counter != 0:
            self.current_player.next.draw()
        self.current_player = self.current_player.next.next
        if not self.current_player.is_human:
            self.current_player.play()
        else:
            from telegram_commands import uno_play_msg
            uno_play_msg(chat_id=self.current_player.chat_id, game=self.current_player.game)

    def play_card(self, card):
        self.deck.beaten(self.last_card)
        self.last_card = card

        if card.value == DRAW_TWO:
            self.draw_counter += 2
            self.skip_next()
            return None
        elif card.value == SKIP:
            self.skip_next()
            return None
        elif card.special == CHOOSE_COLOR:  # ADD INLINE COLOR KEYBOARD
            print("CHOOSING COLOR!")
            bot.send_message(chat_id=self.current_player.chat_id, text="CHOOSING COLOR!")
            if not self.current_player.is_human:
                self.choose_color(random.choice(COLORS))
            else:
                from inline_handle import InlineKeyboardFactory
                bot.send_message(chat_id=self.current_player.chat_id, text="Choose color:",
                                 reply_markup=InlineKeyboardFactory.get_inline_uno_choose_color())
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
            bot.send_message(chat_id=self.current_player.chat_id, text=f"Chosen color {self.last_card.color}")
            return None
        elif card.special not in SPECIAL_CARDS:
            self.next_turn()
            return None
        self.next_turn()
        return None

    def choose_color(self, color: COLORS):
        self.last_card.color = color
        print(f"Chosen color {self.last_card.color}")
        bot.send_message(chat_id=self.current_player.chat_id, text=f"Chosen color {self.last_card.color}")
        self.next_turn()
