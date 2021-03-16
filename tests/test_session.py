import unittest
from staticker.session import Session
from staticker.game import Game
from staticker.player import Player
from staticker.time import Time

class TestSession(unittest.TestCase):

    def setUp(self):
        self.session = Session()
        self.games = [Game() for _ in range(10)]
        self.players = [Player() for _ in range(10)]

    def test_defaults(self):
        self.assertEqual(type(self.session.time), Time)
        
    def test_add(self):
        def run_tests():
            for g in self.games:
                self.assertIn(g.id, self.session.games)
            for p in self.players:
                self.assertIn(p.id, self.session.players)
            self.assertEqual(len(self.session.games), len(self.games))
            self.assertEqual(len(self.session.players), len(self.players))
        
        # TypeErrors
        self.assertRaises(TypeError, self.session.add_games, self.games[0])
        self.assertRaises(TypeError, self.session.add_players, self.players[0])
        
        # Add to session
        self.session.add_games(self.games)
        self.session.add_players(self.players)
        run_tests()
        
        # Should not be added, because already added
        self.session.add_games(self.games)
        self.session.add_players(self.players)
        run_tests()
        
    def test_dump_and_load(self):
        self.session.add_games(self.games)
        self.session.add_players(self.players)
        self.session.set_mode("free")
        self.session.set_playto(10)
        self.session.dump()
        
        session = Session()
        session.load(self.session.id)
        
        self.assertEqual(self.session, session)
        
    def test_playto(self):
        self.assertRaises(TypeError, self.session.set_playto, "str")
        playto = 10
        self.session.set_playto(playto)
        self.assertEqual(self.session.playto, playto)
        
    def test_mode(self):
        self.assertRaises(TypeError, self.session.set_mode, 42)
        self.assertRaises(ValueError, self.session.set_mode, "str")
        
    