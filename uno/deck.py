import card

from card import Card
from random import shuffle
from errors import EmptyDeckError


class Deck:
    def __init__(self):
        self.cards = list()
        self.discard_pile = list()

        # filling
        for color in card.COLORS:
            for value in card.VALUES:
                self.cards.append(Card(color, value))

        for special_card in card.SPECIAL_CARDS:
            self.cards.append(Card(None, None, special=special_card))

        self.shuffle_cards()

    def shuffle_cards(self):
        shuffle(self.cards)

    def get_card(self):
        try:
            card = self.cards.pop()
            return card
        except IndexError:
            if len(self.discard_pile):
                while len(self.discard_pile):
                    self.cards.append(self.discard_pile.pop())
                self.shuffle_cards()
                return self.get_card()
            else:
                raise EmptyDeckError()

    def beaten(self, card):
        self.discard_pile.append(card)
