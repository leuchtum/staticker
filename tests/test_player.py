import unittest
from staticker.player import Player

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player()

    def test_default_values(self):
        self.assertNotEqual(len(self.player.id), 0)
        self.assertIs(self.player.name, None)
        self.assertEqual(len(self.player.games), 0)
        self.assertEqual(self.player._tablename, "player")

    def test_set_name(self):
        name = "TESTNAME"
        self.player.set_name(name)
        self.assertEqual(name, self.player.name)
        with self.assertRaises(TypeError):
            self.player.set_name(999)

    def test_add_game(self):
        game_id = "TEST_ID"
        self.player.add_game(game_id)
        self.assertTrue(game_id in self.player.games)
        with self.assertRaises(TypeError):
            self.player.add_game(999)

    def test_del_game(self):
        game_id = "TEST_ID"
        self.player.add_game(game_id)
        self.assertTrue(game_id in self.player.games)
        self.player.del_game(game_id)
        self.assertFalse(game_id in self.player.games)
        with self.assertRaises(TypeError):
            self.player.add_game(999)

    def test_dump_and_load(self):
        name = "TESTNAME"
        game_id = "TEST_ID"

        self.player.set_name(name)
        self.player.add_game(game_id)
        self.player.dump()

        p = Player()
        p.load(self.player.id)

        self.assertEqual(p.id, self.player.id)
        self.assertEqual(p.name, self.player.name)
        self.assertEqual(p.games, self.player.games)
        with self.assertRaises(TypeError):
            self.player.load(999)