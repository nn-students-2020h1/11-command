import unittest

from card import Card
from deck import Deck
from errors import EmptyDeckError


class TestDeck(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()

    def tearDown(self):
        self.deck = Deck()

    def test_empty(self):
        with self.assertRaises(EmptyDeckError):
            self.deck.cards = list()
            self.deck.get_card()

    def test_shuffle(self):
        self.prev = self.deck.cards
        self.deck.shuffle_cards()
        self.assertListEqual(self.prev, self.deck.cards)

    def test_beaten(self):
        self.deck.beaten(self.deck.cards[0])
        self.assertNotEqual(self.deck.discard_pile, list())

    def test_beaten_empty(self):
        self.assertListEqual(self.deck.discard_pile, [])

    def test_get_card(self):
        self.testCard = self.deck.get_card()
        self.assertNotIn(self.testCard, self.deck.cards)
