import unittest
import pymongo
import mongomock
import database

import telegram_commands
import uno.game as game
from unittest import mock
from uno.card import GREEN
from uno.game import Game
from uno.player import Player


def simple_func(**kwargs):
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
    def test_next_turn_perfect(self):
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
    def test_next_turn_draw(self):
        self.player_1 = Player(game=self.game, chat_id=0, is_human=False, name="John Doe")
        self.player_2 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 1")
        self.game.add_player(player=self.player_1)
        self.game.add_player(player=self.player_2)
        self.game.draw_counter = 1  # first player draws one card
        self.game.next_turn()
        self.assertEqual(self.game.current_player, self.player_2)

    @mock.patch.object(game.Player, 'play', lambda self: simple_func())
    def test_next_turn_human(self):
        self.player_1 = Player(game=self.game, chat_id=0, is_human=True, name="John Doe")
        self.player_2 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 1")
        self.game.add_player(player=self.player_1)
        self.game.add_player(player=self.player_2)
        with mock.patch('telegram_commands.uno_play_msg', return_value=None):
            self.game.next_turn()
            self.assertEqual(self.game.round, 2)

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

    def test_skip_next_draw(self):
        self.player_1 = Player(game=self.game, chat_id=0, is_human=False, name="John Doe")
        self.player_2 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 1")
        self.game.add_player(player=self.player_1)
        self.game.add_player(player=self.player_2)
        self.game.draw_counter = 1
        with mock.patch('telegram_commands.uno_play_msg', return_value=None):
            self.game.skip_next()
            self.assertEqual(self.player_2.cards.__len__(), 8)

    def test_skip_next_human(self):
        self.player_1 = Player(game=self.game, chat_id=0, is_human=True, name="John Doe")
        self.player_2 = Player(game=self.game, chat_id=0, is_human=False, name="Bot 1")
        self.game.add_player(player=self.player_1)
        self.game.add_player(player=self.player_2)
        self.game.draw_counter = 1
        with mock.patch('telegram_commands.bot') as mock_bot:
            mock_bot.send_message.return_value = None
            self.game.skip_next()
            self.assertEqual(self.game.players[1].cards.__len__(), 8)

    @mock.patch.object(game.Player, 'play', lambda self: simple_func())
    def test_play_card(self):
        with mock.patch('uno.game.Game.get_board', return_value=None):
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

    @mongomock.patch(servers=(('testserver.com', 27017),))
    def test_get_board(self):
        self.player_1 = Player(game=self.game, chat_id=0, is_human=False, name="John Doe")
        self.game.add_player(player=self.player_1)
        with mock.patch('database.pymongo.MongoClient') as mock_client:
            mock_client.return_value = pymongo.MongoClient('testserver.com')
            self.db = database.UserDataBase()
            with mock.patch('uno.game.Image.new') as mock_new_img:
                mock_new_img.paste.return_value = None
                mock_new_img.save.return_value = None
                with mock.patch('uno.game.Image.open') as mock_img:
                    mock_img.width = 480
                    mock_img.length = 860
                    mock_img.convert.return_value = None
                    self.db.db_user_actions = pymongo.MongoClient('testserver.com')['user_actions']
                    with mock.patch('auxiliary_functions.db_user_action', new=self.db):
                        with mock.patch('telegram_commands.bot') as mock_bot:
                            mock_bot.send_message.return_value = None
                            with mock.patch('builtins.open', return_value=None):
                                with mock.patch('uno.game.bot.send_photo', return_value=None):
                                    self.assertIn(self.game.get_board(), self.game.temp_messages)
