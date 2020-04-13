import unittest
from card import Card


class TestCard(unittest.TestCase):
    def setUp(self):
        self.card = Card()

    def tearDown(self):
        self.card.color = None
        self.card.value = None
        self.card.special = None

    def test_reveal_common(self):
        self.card.color = RED
        self.card.value = ONE
        self.assertEqual(self.card.reveal, [RED, ONE])
