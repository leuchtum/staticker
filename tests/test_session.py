from staticker.session import Session
from staticker.game import Game
from staticker.player import Player
from staticker.time import Time
import pytest

@pytest.fixture()
def setup():
    session = Session()
    games = [Game() for _ in range(10)]
    players = [Player() for _ in range(10)]
    return session, games, players

def test_defaults(setup):
    session, games, players = setup
    assert type(session.time) == Time
    
def test_add(setup):
    def run_tests(session, games, players):
        for g in games:
            assert g.id in session.game_ids
        for p in players:
            assert p.id in session.player_ids
        assert len(session.game_ids) == len(games)
        assert len(session.player_ids) == len(players)
    
    session, games, players = setup
    
    # TypeErrors
    with pytest.raises(TypeError):
        session.add_games(games[0])
    with pytest.raises(TypeError):
        session.add_players(players[0])
    
    # Add to session
    session.add_games(games)
    session.add_players(players)
    run_tests(session, games, players)
    
    # Should not be added, because already added
    session.add_games(games)
    session.add_players(players)
    run_tests(session, games, players)
    
def test_dump_and_load(setup):
    session, games, players = setup
    
    session.add_games(games)
    session.add_players(players)
    session.set_mode("free")
    session.set_playto(10)
    
    for p in players:
        p.dump()
    for g in games:
        g.dump()
    session.dump()  
    
    s = Session()
    s.load(session.id)
    
    assert s == session
    
def test_playto(setup):
    session, games, players = setup
    
    with pytest.raises(TypeError):
        session.set_playto("str")
    playto = 10
    session.set_playto(playto)
    assert session.playto == playto
    
def test_mode(setup):
    session, games, players = setup
    
    with pytest.raises(TypeError):
        session.set_mode(42)
    with pytest.raises(ValueError):
        session.set_mode("str")
    
