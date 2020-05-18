import unittest

from uno.card import Card, RED, ONE, DRAW_FOUR


class TestCard(unittest.TestCase):
    def setUp(self):
        self.card = Card(None, None)

    def tearDown(self):
        self.card.color = None
        self.card.value = None
        self.card.special = None

    def test_reveal_common(self):
        self.card = Card(RED, ONE)
        self.assertEqual(self.card.reveal(), [RED, ONE])

    def test_reveal_special(self):
        self.card.special = DRAW_FOUR
        self.assertEqual(self.card.reveal(), DRAW_FOUR)
