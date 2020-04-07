import card

from errors import EmptyDeckError


class Player:
    def __init__(self, game, is_human=False):
        self.cards = list()
        self.game = game
        self.is_human = is_human

        try:
            for i in range(7):
                self.cards.append(self.game.deck.draw())
        except DeckEmptyError:
            for card in self.cards:
                self.game.deck.dismiss(card)
