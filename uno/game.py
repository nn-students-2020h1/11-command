from deck import Deck
from player import Player
from card import COLORS, VALUES
import card


class Game:
    current_player = None
    choosing_color = False
    started = False
    draw_counter = 0

    def __init__(self):
        self.user = Player(isHuman=True)
        self.computer = Player(isHuman=False)
        self.last_card = None

        while not self.last_card or self.last_card.special:
            self.deck = Deck()
            self.last_card = self.deck.get_card()

    def next_turn(self):
        self.current_player = self.computer if self.current_player == self.user else self.user

    def play_card(self, card):
        self.deck.beaten(self.last_card)
        self.last_card = card

        if card.value == VALUES.DRAW_TWO:
            draw_counter += 2
        elif card.value == VALUES.SKIP:
            self.next_turn()
            self.next_turn()

    def choose_color(self, color: COLORS):
        self.last_card.color = color
