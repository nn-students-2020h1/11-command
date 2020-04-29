import unittest
from unittest.mock import patch
import telegram_commands


class TestFact(unittest.TestCase):
    def test_bad_request(self):
        with patch('telegram_commands.requests.get') as mock_get:
            mock_get.return_value.ok = False
            fact = telegram_commands.get_quote("https://cat-fact.herokuapp.com/facts")
            self.assertEqual(fact, ["You're awesome.", "Our ConnectionError"])

    def test_ok_request(self):
        with patch('telegram_commands.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {"all": [{"text": "test", "user": {"name": {"first": "test",
                                                                                                  "last": "test"}}}]}
            fact = telegram_commands.get_quote("https://cat-fact.herokuapp.com/facts")
        self.assertEqual(fact, ["<i>test</i>", "<b>Author: test test</b>"])

    def test_exception_request(self):
        with patch('telegram_commands.requests.get') as mock_get:
            mock_get.side_effect = ConnectionError
            fact = telegram_commands.get_quote("https://cat-fact.herokuapp.com/facts")
        self.assertEqual(fact, ["You're awesome.", "Our ConnectionError"])

    def test_bad_fact_format(self):
        with patch('telegram_commands.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {"what?": "nothing..."}
            fact = telegram_commands.get_quote("https://cat-fact.herokuapp.com/facts")
        self.assertEqual(fact, ["You're awesome.", "Our KeyError"])

    def test_no_fact(self):
        with patch('telegram_commands.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value = None
            fact = telegram_commands.get_quote("https://cat-fact.herokuapp.com/facts")
        self.assertEqual(fact, ["You're awesome.", "Our ConnectionError"])
