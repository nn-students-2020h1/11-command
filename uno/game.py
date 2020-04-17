from deck import Deck
from player import Player
from card import COLORS, VALUES, SPECIAL_CARDS
import card
import random

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

    def skip_next(self):
        if self.draw_counter != 0:
            self.current_player.next.draw()
        self.current_player = self.current_player.next.next

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
        elif card.special == CHOOSE_COLOR:
            print("CHOOSING COLOR!")
            if not self.current_player.is_human:
                self.choose_color(random.choice(COLORS))
            else:
                color = input("Color: ")
                self.choose_color(color)
            print(f"Chosen color {self.last_card.color}")
            return None
        elif card.special == DRAW_FOUR:
            self.draw_counter += 4
            if not self.current_player.is_human:
                self.choose_color(random.choice(COLORS))
            else:
                color = input("Color: ")
                self.choose_color(color)
            print(f"Chosen color {self.last_card.color}")
            return None
        elif card.special not in SPECIAL_CARDS:
            self.next_turn()
            return None
        self.next_turn()
        return None

    def choose_color(self, color: COLORS):
        self.last_card.color = color
        self.next_turn()
