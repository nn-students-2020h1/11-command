from uno.errors import EmptyDeckError, WrongCardError
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Bot
from setup import TOKEN, PROXY

bot = Bot(
    token=TOKEN,
    base_url=PROXY,  # delete it if connection via VPN
)


class Player:
    def __init__(self, chat_id, game, is_human=False, name="Default Name"):
        self.cards = list()
        self.game = game
        self.is_human = is_human
        self.name = name
        self.next = self
        self.prev = self
        self.chat_id = chat_id

        try:
            for i in range(7):
                self.cards.append(self.game.deck.get_card())
        except EmptyDeckError:
            for card in self.cards:
                self.game.deck.beaten(card)

    def view_deck(self) -> str:
        index = 0
        msg = ""
        for playable_card in self.cards:
            msg += f"{index}. Color: {playable_card.color}, Value: {playable_card.value}, Special: {playable_card.special}\n"
            index += 1
        return msg

    def deck_choose_keyboard(self) -> InlineKeyboardMarkup:
        index = 0
        keyboard = []
        for playable_card in self.cards:
            if playable_card.color == self.game.last_card.color or playable_card.value == self.game.last_card.value or playable_card.special:  # noqa: E501  # TODO: if statement's length cannot be reduced
                button = InlineKeyboardButton(f"{index}. {playable_card.color}, {playable_card.value}, {playable_card.special}",  # noqa: E501
                                              callback_data=index)
                keyboard.append([button])
            index += 1
        keyboard.append([InlineKeyboardButton("DRAW ONE", callback_data="callback_uno_draw_one")])
        return InlineKeyboardMarkup(keyboard)

    def draw(self):
        amount = 1 if self.game.draw_counter == 0 else self.game.draw_counter
        try:
            for i in range(amount):
                self.cards.append(self.game.deck.get_card())

        except EmptyDeckError:
            raise

        finally:
            self.game.draw_counter = 0

    def play(self, card=None):
        if self.is_human:
            if card.color == self.game.last_card.color or card.value == self.game.last_card.value or card.special:
                self.cards.remove(card)
                if self.cards.__len__() == 0:
                    bot.send_message(chat_id=self.chat_id, text="You won!")
                    self.game.started = False
                self.game.play_card(card)

            else:
                raise WrongCardError
        else:
            if self.game.started:
                for playable_card in self.cards:
                    if playable_card.color == self.game.last_card.color or playable_card.value == self.game.last_card.value or playable_card.special is not None:  # noqa: E501  # TODO: will fix this later
                        self.cards.remove(playable_card)
                        self.game.play_card(playable_card)

                        if self.cards.__len__() == 0:
                            bot.send_message(chat_id=self.chat_id, text=f"{self.name} won!")
                            self.game.started = False
                        return None
                self.draw()
                self.game.next_turn()
