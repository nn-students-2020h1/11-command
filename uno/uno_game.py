from game import Game
from player import Player


class GameManager:
    game = Game()
    user = Player(game=game, is_human=False, name='Вася Пупкин')
    computer = Player(game=game, is_human=False, name='Дед')
    game.add_player(user)
    game.add_player(computer)
    game.started = True
    while game.started:
        if game.current_player.is_human:
            print(game.current_player.next.is_human)
            print(f"Computer has {computer.cards.__len__()} cards")
            print(f"Play the special card or {game.last_card.color} card or value {game.last_card.value} card. Your deck:")
            user.view_deck()
            msg = input("Type index or X (draw 1): ")
            if msg == "X":
                user.draw()
                game.next_turn()
            else:
                user.play(user.cards[int(msg)])
        else:
            game.current_player.play()
            print(f"{game.current_player.name} has {game.current_player.cards.__len__()} cards")
