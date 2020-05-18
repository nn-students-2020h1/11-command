import unittest

from uno.card import Card
from uno.player import Player
from uno.game import Game
from uno.errors import EmptyDeckError, WrongCardError


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.player = Player(game=self.game, chat_id=0)
        self.game.add_player(self.player)

    def tearDown(self):
        self.game = Game()
        self.player = Player(game=self.game, chat_id=0)
        self.game.add_player(self.player)

    def test_not_human(self):
        self.assertFalse(self.player.is_human)

    def test_empty_pile(self):
        self.game.deck.cards = list()
        with self.assertRaises(EmptyDeckError):
            self.player.draw()

    def test_draw(self):
        self.card_count = self.player.cards.__len__()
        self.player.draw()
        self.assertGreater(self.player.cards.__len__(), self.card_count)

    def test_wrong_card(self):
        self.player.is_human = True
        self.wrong_card = Card(color="wrong", value="wrong")
        with self.assertRaises(WrongCardError):
            self.player.play(self.wrong_card)
