import unittest
import sys

"""artificial tests"""


class TestHomeWork(unittest.TestCase):

    def test_sum_two_number(self):
        self.assertEqual((sum_two_numbers(0, 0)), 0)
        self.assertEqual((sum_two_numbers(1, 1)), 2)
        self.assertEqual((sum_two_numbers(-10, 10)), 0)
        self.assertEqual((sum_two_numbers(sys.maxsize, -sys.maxsize)), 0)
        self.assertEqual((sum_two_numbers(88888889, 11111111)), 100000000)

    def test_bit_shift_left(self):
        self.assertEqual((bit_shift_left(1, 0)), 1)
        self.assertEqual((bit_shift_left(1, 1)), 2)
        self.assertEqual((bit_shift_left(3, 1)), 6)
        self.assertEqual((bit_shift_left(1, 20)), 1048576)

    def test_count_words(self):
        self.assertEqual((word_in_stroke('a b c')), 3)
        self.assertEqual((word_in_stroke('    a  ')), 1)
        self.assertEqual((word_in_stroke(' ')), 0)
        self.assertEqual((word_in_stroke('')), 0)
        self.assertEqual((word_in_stroke('asd1 12312 adssa <>!@#%^&*() + - ')), 2)
        self.assertEqual((word_in_stroke('abcdf')), 1)
        self.assertEqual((word_in_stroke('康熙字典體'*1010000)), 1)
        self.assertEqual((word_in_stroke('康 熙 字 典 體')), 5)
        self.assertEqual((word_in_stroke(' 康 熙 字 典 體 '*100)), 500)


def sum_two_numbers(a, b):
    return a + b


def bit_shift_left(a, b):
    return a << b


def word_in_stroke(stroke):
    flag = False
    count = 0
    for i in stroke:
        if i.isalpha() and not flag:
            count += 1
            flag = True
        elif i == ' ':
            flag = False
    return count


if __name__ == '__main__':
    unittest.main()
