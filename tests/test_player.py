from staticker.player import Player
import pytest

@pytest.fixture()
def setup():
    name = "TESTNAME"
    game_id = "TEST_ID"
    
    player = Player()
    player.set_name(name)
    player.add_game(game_id)
    
    return player, name, game_id

def test_default_values(setup):
    player, name, game_id = setup

    assert len(player.id) != 0
    assert player._tablename == "player"

def test_set_name(setup):
    player, name, game_id = setup
    
    name = "TESTNAME"
    player.set_name(name)
    assert name == player.name
    with pytest.raises(TypeError):
        player.set_name(999)

def test_add_game(setup):
    player, name, game_id = setup
    
    assert game_id in player.games
    with pytest.raises(TypeError):
        player.add_game(999)

def test_del_game(setup):
    player, name, game_id = setup

    assert game_id in player.games
    player.del_game(game_id)
    assert game_id not in player.games
    with pytest.raises(TypeError):
        player.add_game(999)

def test_dump_and_load(setup):
    player, name, game_id = setup
    
    player.dump()

    p = Player()
    p.load(player.id)

    assert p.id == player.id
    assert p.name == player.name
    assert p.games == player.games
    with pytest.raises(TypeError):
        player.load(999)