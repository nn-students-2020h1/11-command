import card

from errors import EmptyDeckError, WrongCardError


class Player:
    def __init__(self, game, is_human=False, name="Default Name"):
        self.cards = list()
        self.game = game
        self.is_human = is_human
        self.name = name
        self.next = self
        self.prev = self

        try:
            for i in range(7):
                self.cards.append(self.game.deck.get_card())
        except EmptyDeckError:
            for card in self.cards:
                self.game.deck.beaten(card)

    def view_deck(self):
        index = 0
        for playable_card in self.cards:
            print(f"{index}. Color: {playable_card.color}, Value: {playable_card.value}, Special: {playable_card.special}")
            index += 1

    def draw(self):
        amount = 1 if self.game.draw_counter == 0 else self.game.draw_counter
        try:
            for i in range(amount):
                self.cards.append(self.game.deck.get_card())

        except EmptyDeckError:
            raise

        finally:
            self.game.draw_counter = 0

    def play(self, card=None):
        if self.is_human:
            if card.color == self.game.last_card.color or card.value == self.game.last_card.value or card.special:
                self.game.play_card(card)
                self.cards.remove(card)
                print(f"You played card {card.color} {card.value} {card.special}. Your deck:")
                self.view_deck()

                if self.cards.__len__() == 0:
                    print("You won!")
                    self.game.started = False

            else:
                raise WrongCardError
        else:
            for playable_card in self.cards:
                if playable_card.color == self.game.last_card.color or playable_card.value == self.game.last_card.value or playable_card.special is not None:
                    self.game.play_card(playable_card)
                    print(f"{self.name} played card {playable_card.color} {playable_card.value} {playable_card.special}.")
                    self.cards.remove(playable_card)
                    if self.cards.__len__() == 0:
                        print(self.name)
                        self.game.started = False
                    return None
            self.draw()
            self.game.next_turn()
