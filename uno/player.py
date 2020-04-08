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

    def draw(self):
        amount = 1 if game.draw_counter == 0 else game.draw_counter
        try:
            for i in range(amount):
                self.cards.append(self.game.deck.get_card())

        except EmptyDeckError:
            raise

        finally:
            self.game.draw_counter = 0

    def play(self, card):
        if card.color == self.game.last_card.color or card.value == self.game.last_card.value or self.game.last_card.special:
            self.game.play_card(card)
            self.cards.remove(card)
        else:
            print("Wrong card!")
