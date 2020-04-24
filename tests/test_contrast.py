import unittest
import telegram
from unittest import mock
from unittest.mock import patch
from image_handler import get_contrast_img
from telegram_commands import command_handle_contrast
import auxiliary_functions
from PIL import Image
import os


def mock_decorator(func):
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner


class TestContrast(unittest.TestCase):

    def test_change_contrast(self):
        os.chdir('..')
        print(os.getcwd())
        get_contrast_img(5.0, "initial_user_images/initial.jpg", "result_user_images/res.jpg")
        self.assertNotEqual(Image.open("initial_user_images/initial.jpg"), Image.open("result_user_images/res.jpg"))

    def test_no_image(self):
        with patch('telegram.Update') as mock_update:
            mock_update.message.chat.id = 0
        with patch("telegram_commands.bot.send_photo") as mock_image:
            mock_image.side_effect = FileNotFoundError
            self.assertEqual(command_handle_contrast(mock_update), "Initial image wasn't found.")
