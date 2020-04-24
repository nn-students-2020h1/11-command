import unittest
import initial_user_images, result_user_images
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

    def test_no_img_to_change_contrast(self):
        self.assertEqual("File not found.", get_contrast_img(5.0, "test", "test"))

    def test_no_image_to_send(self):
        with patch('telegram.Update') as mock_update:
            mock_update.message.chat.id = 0
        with patch("telegram_commands.bot.send_photo") as mock_image:
            mock_image.side_effect = FileNotFoundError
            self.assertEqual(command_handle_contrast(mock_update), "Initial image wasn't found.")
