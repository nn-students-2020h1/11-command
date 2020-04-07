RED = "color_red"
GREEN = "color_green"
BLUE = "color_blue"
YELLOW = "color_yellow"
ALL = "color_independence"

COLORS = (RED, GREEN, BLUE, YELLOW)

ONE = '1'
TWO = '2'
THREE = '3'
FOUR = '4'
FIVE = '5'
SIX = '6'
SEVEN = '7'
EIGHT = '8'
NINE = '9'
DRAW_TWO = 'draw_2'
SKIP = 'skip'

VALUES = (ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, DRAW_TWO, SKIP)

SPECIAL_CARDS = {DRAW_FOUR, CHOOSE_COLOR}


class Card:
    def __init__(self, color, value, special=False):
        self.color = color
        self.value = value
        self.special = special