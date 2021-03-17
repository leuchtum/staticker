from staticker.player import Player
from staticker.game import Slot, Game
import pytest

@pytest.fixture()
def setup():
    p1 = Player()
    p1.set_name("P1")

    p2 = Player()
    p2.set_name("P2")

    game = Game() # Order is important
    game.black.set_player([p1])
    game.white.set_player([p2])
    
    playto = 10
    game.set_playto(playto)
    
    return game, playto, p1, p2

def test_default_values():
    slot = Slot()
    assert slot.goal == 0
    assert slot.own == 0
    assert slot.foul == 0
    assert slot.id is None
    assert slot._playto is 0

def test_init(setup):
    game, playto, p1, p2 = setup
    
    p1 = Player()
    p1.set_name("P1")

    p2 = Player()
    p2.set_name("P2")

    p1.dump()
    p2.dump()

    game = Game() # Order is important
    game.black.set_player([p1])
    game.white.set_player([p2])
    game.set_playto(10)

    assert game.black.single.id == p1.id
    assert game.white.single.id == p2.id

    assert game.black.single._player == p1
    assert game.white.single._player == p2

    assert game.black.single._player.name == p1.name
    assert game.white.single._player.name == p2.name

    assert game.black.single._playto == game.playto
    assert game.white.single._playto == game.playto

def test_get_name(setup):
    game, playto, p1, p2 = setup
    
    p1 = Player()
    p1.set_name("P1")

    p2 = Player()
    p2.set_name("P2")

    game = Game() # Order is important
    game.black.set_player([p1])
    game.white.set_player([p2])

    assert game.black.single._player.name == p1.name
    assert game.white.single._player.name == p2.name

def test_set_playto(setup):
    game, playto, p1, p2 = setup
    
    assert game.black.single._playto == 10
    assert game.white.single._playto == 10

def test_add_and_del(setup):
    game, playto, p1, p2 = setup

    game.black.single.del_goal()
    game.black.single.del_owner()
    game.black.single.del_foul()

    assert game.black.single.goal == 0
    assert game.black.single.own == 0
    assert game.black.single.foul == 0

    for i in range(1, playto + 1):
        game.black.single.add_goal()
        game.black.single.add_owner()
        game.black.single.add_foul()

    assert game.black.single.goal == playto
    assert game.black.single.own == playto
    assert game.black.single.foul == i