import unittest
import os
"""Useful tests"""


class TestHomeWork(unittest.TestCase):

    def setUp(self):
        self.files = get_list_of_files()

    def test_exist_necessary_files(self):
        self.assertIn('chat_bot_template.py', str(self.files))
        self.assertIn('auxiliary_functions.py', str(self.files))
        self.assertIn('Covid_19.py', str(self.files))
        self.assertIn('image_handler.py', str(self.files))
        self.assertIn('image_handler.py', str(self.files))
        self.assertIn('inline_handle.py', str(self.files))
        self.assertIn('setup.py', str(self.files))
        self.assertIn('telegram_commands.py', str(self.files))


def get_list_of_files():
    path = os.path.abspath(os.curdir)

    path = path.replace(r'unit-tests', "")
    path = path[:-1]

    for top, dirs, files in os.walk(path):
        return files


if __name__ == '__main__':
    unittest.main()