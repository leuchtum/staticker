from staticker.core import Player, Event, Game
import random
from peewee import fn

def get_random_name():
    names = [
        "Alpha",
        "Bravo",
        "Charlie",
        "Delta",
        "Echo",
        "Foxtrot",
        "Golf",
        "Hotel",
        "India",
        "Julia",
        "Kilo",
        "Lima",
        "Mike",
        "November",
        "Oscar",
        "Papa",
        "Quebec",
        "Romeo",
        "Sierra",
        "Tango",
        "Uniform",
        "Victor",
        "Wiskey",
        "X-Ray",
        "Yankee",
        "Zulu"
    ]
    decimals = random.choices([str(i) for i in range(10)], k=8)
    name = random.choices(names, k=2)
    return "_".join(["_".join(name), "".join(decimals)])


def get_random_player():
    return Player.select().order_by(fn.Random()).limit(1).get()


def get_random_game():
    return Game.select().order_by(fn.Random()).limit(1).get()


def new_players(n):
    for _ in range(n):
        p = Player(name=get_random_name())
        p.save()


def play_synthetic_event(n_player, n_games):
    player = []
    while len(player) < n_player:
        p = get_random_player()
        if p not in player:
            player.append(p)

    ev = Event(mode="free")
    ev.activate()
    ev.add_player(player)

    for _ in range(n_games):
        n_b = random.choice([1, 2])
        n_w = random.choice([1, 2])

        equals = True
        while equals:
            p_b = random.choices(player, k=n_b)
            p_w = random.choices(player, k=n_w)
            equals = any(p in p_w for p in p_b)

        g = Game()
        g.add_player(p_b, p_w)
        ev.add_game(g)

        while not g.finished:
            side = random.choice(["b", "w"])
            slot = random.choice(["def", "off", "off"])
            how = random.choice(["g", "g", "g", "g", "o"])
            if how == "g":
                g.goal(side, slot)
            elif how == "o":
                g.owner(side, slot)
        
        print(f"Ev: {ev.id} | Game: {g.id}")
    ev.deactivate()


if __name__ == '__main__':
    n_new_players = 5
    n_games = 20

    new_players(n_new_players)

    play_synthetic_event(4, n_games)
    print("finished")
