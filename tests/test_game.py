from staticker.player import Player
from staticker.game import Game, Side
from staticker.time import Time
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
        
def test_init(setup):
    game, playto, p1, p2, p3 = setup 
    
    assert type(game.time) == Time
    assert type(game.black) == Side
    assert type(game.white) == Side
    
def test_dump_and_load(setup):
    game, playto, p1, p2, p3 = setup 
    
    game.black.single.add_goal()
    game.white.offense.add_goal()
    game.white.defense.add_goal()
    
    game.dump()
    p1.dump()
    p2.dump()
    p3.dump()
    
    g = Game()
    g.load(game.id)
    
    assert game == g
    assert game.black.single._playto == playto
    assert game.white.defense._playto == playto
    assert game.white.offense._playto == playto
    
def test_set_playto(setup):
    game, playto, p1, p2, p3 = setup 
    
    assert game.playto == playto
    assert game.black.single._playto == playto
    assert game.white.defense._playto == playto
    assert game.white.offense._playto == playto
    
def test_get_score(setup):
    game, playto, p1, p2, p3 = setup 
    
    for _ in range(3):
        game.black.single.add_goal()
        game.white.defense.add_goal()
        game.white.offense.add_goal()
        
    score = game.get_score()
    assert score["score_black"] == 3
    assert score["score_white"] == 6
    
def test_is_finished(setup):      
    game, playto, p1, p2, p3 = setup 
    
    assert not game.is_finished()
    
    for _ in range(int(playto/2)):
        game.black.single.add_goal()
        game.white.defense.add_goal()
        game.white.offense.add_goal()
        
    assert game.is_finished()
        
def test_get_slot_by_id(setup):
    game, playto, p1, p2, p3 = setup 
    
    slot1 = game.black.single
    slot2 = game.white.defense
    slot3 = game.white.offense
    
    assert game.get_slot_by_id(p1.id) == slot1
    assert game.get_slot_by_id(p2.id) == slot2
    assert game.get_slot_by_id(p3.id) == slot3
    
def test_get_side_by_id(setup):
    game, playto, p1, p2, p3 = setup 
    
    black = game.black
    white = game.white
    
    assert game.get_side_by_id(p1.id) == black
    assert game.get_side_by_id(p2.id) == white
    assert game.get_side_by_id(p3.id) == white
    
def test_get_position_result(setup):
    game, playto, p1, p2, p3 = setup 
    #TODO Implement

def test_flip_sides(setup):
    game, playto, p1, p2, p3 = setup 
    
    black = game.black
    white = game.white
    
    game.flip_sides()
    
    assert game.white == black
    assert game.black == white
        
            
        
        