from staticker.player import Player
from staticker.game import Game, Slot, Side
import pytest

@pytest.fixture()
def setup():
    game = Game()
    
    p1 = Player()
    p1.set_name("P1")

    p2 = Player()
    p2.set_name("P2")

    p3 = Player()
    p3.set_name("P3")

    game.black.set_player([p1])
    game.white.set_player([p2, p3])

    playto = 10
    game.set_playto(playto)
    
    return game, playto, p1, p2, p3

def test_init():
    side = Side()
    
    assert side._mode is None
    assert side.single is None
    assert side.defense is None
    assert side.offense is None

def test_set_player(setup):
    game, playto, p1, p2, p3 = setup 
    
    # Order is important
    game.black.set_player([p1])
    game.white.set_player([p2, p3])

    assert type(game.black.single) is Slot
    assert game.black.defense is None
    assert game.black.offense is None

    assert game.white.single is None
    assert type(game.white.defense) is Slot
    assert type(game.white.offense) is Slot

    assert game.black._mode is "single"
    assert game.white._mode is "multi"

def test_get_goals_owners_fouls(setup):
    game, playto, p1, p2, p3 = setup 
    
    # Order is important
    game.black.set_player([p1])
    game.white.set_player([p2, p3])

    playto = 10
    game.set_playto(playto)

    game.black.single.add_goal()
    game.black.single.add_owner()
    game.black.single.add_foul()

    game.white.defense.add_goal()
    game.white.defense.add_owner()
    game.white.defense.add_foul()

    game.white.offense.add_goal()
    game.white.offense.add_owner()
    game.white.offense.add_foul()

    assert game.black.get_goals() == 1
    assert game.black.get_owners() == 1
    assert game.black.get_fouls() == 1

    assert game.white.get_goals() == 2
    assert game.white.get_owners() == 2
    assert game.white.get_fouls() == 2

def test_flip_slots(setup):
    game, playto, p1, p2, p3 = setup 
    
    #Order is important
    game.black.set_player([p1])
    game.white.set_player([p2, p3])

    slot1 = game.white.defense
    slot2 = game.white.offense

    game.white.flip_slots()

    assert game.white.defense is slot2
    assert game.white.offense is slot1