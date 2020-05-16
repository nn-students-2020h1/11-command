import unittest

import uno.game as game
from unittest import mock
from uno.card import GREEN
from uno.game import Game
from uno.player import Player


def simple_func(chat_id=None, text=None):
    pass


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        self.game = Game()

    def test_add_player(self):
        self.player = Player(game=self.game, chat_id=0, is_human=True, name="John Doe")
        self.game.add_player(player=self.player)
        self.assertIn(self.player, self.game.players)

    def test_is_player(self):
        self.player = Player(game=self.game, chat_id=0, is_human=True, name="John Doe")
        self.game.add_player(player=self.player)
        self.assertIsInstance(self.game.current_player, Player)

    @mock.patch.object(game.Player, 'play', lambda self: simple_func())
    def test_next_turn(self):
        self.player_1 = Player(game=self.game, chat_id=0, is_human=False, name="John Doe")
        self.player_2 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 1")
        self.player_3 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 2")
        self.game.add_player(player=self.player_1)
        self.game.add_player(player=self.player_2)
        self.game.add_player(player=self.player_3)
        for i in range(5):
            self.game.next_turn()
        self.assertEqual(self.game.current_player, self.player_3)

    @mock.patch.object(game.Player, 'play', lambda self: simple_func())
    def test_skip_next(self):
        self.player_1 = Player(game=self.game, chat_id=0, is_human=False, name="John Doe")
        self.player_2 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 1")
        self.player_3 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 2")
        self.game.add_player(player=self.player_1)
        self.game.add_player(player=self.player_2)
        self.game.add_player(player=self.player_3)
        self.game.skip_next()
        self.assertEqual(self.game.current_player, self.player_3)

    @mock.patch.object(game.Player, 'play', lambda self: simple_func())
    def test_play_card(self):
        self.player_1 = Player(game=self.game, chat_id=0, is_human=False, name="John Doe")
        self.player_2 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 1")
        self.game.add_player(player=self.player_1)
        self.game.add_player(player=self.player_2)
        self.last = self.game.last_card
        self.game.play_card(self.game.last_card)
        self.assertIn(self.last, self.game.deck.discard_pile)

    @mock.patch.object(game.Player, 'play', lambda self: simple_func())
    def test_choose_color(self):
        with mock.patch('uno.game.bot') as mock_bot:
            mock_bot.send_message.return_value = None
            self.player_1 = Player(game=self.game, chat_id=0, is_human=False, name="John Doe")
            self.game.add_player(player=self.player_1)
            self.game.choose_color(GREEN)
            self.assertIs(self.game.last_card.color, GREEN)
