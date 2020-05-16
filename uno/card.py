from PIL import Image

RED = "r"
GREEN = "g"
BLUE = "b"
YELLOW = "y"

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
DRAW_FOUR = 'draw_4'
CHOOSE_COLOR = 'choose_color'
SKIP = 'skip'

VALUES = (ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, DRAW_TWO, SKIP)

SPECIAL_CARDS = {DRAW_FOUR, CHOOSE_COLOR}


class Card:
    def __init__(self, color, value, special=None):
        self.color = color
        self.value = value
        self.special = special

    def reveal(self):
        if self.special:
            return self.special
        else:
            return [self.color, self.value]

    def get_img(self) -> Image:
        if self.value and self.value != DRAW_TWO:
            return Image.open(f"uno/images/{self.color}_{self.value}.png")
        elif self.value == DRAW_TWO:
            return Image.open(f"uno/images/{self.color}_draw.png")
        elif self.value == SKIP:
            return Image.open(f"uno/images/{self.color}_skip.png")
        elif self.special == DRAW_FOUR:
            return Image.open("uno/images/draw_four.png")
        elif self.last_card.special == CHOOSE_COLOR:
            return Image.open("uno/images/choosecolor.png")
