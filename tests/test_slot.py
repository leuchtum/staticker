import unittest
from staticker.player import Player
from staticker.game import Slot, Game

class SlotPlayer(unittest.TestCase):

    def setUp(self):
        self.slot = Slot()

    def test_default_values(self):
        self.assertEqual(self.slot.goal, 0)
        self.assertEqual(self.slot.own, 0)
        self.assertEqual(self.slot.foul, 0)
        self.assertIs(self.slot.id, None)
        self.assertIs(self.slot._playto, 0)

    def test_init(self):
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

        self.assertEqual(game.black.single.id, p1.id)
        self.assertEqual(game.white.single.id, p2.id)

        self.assertEqual(game.black.single._player, p1)
        self.assertEqual(game.white.single._player, p2)

        self.assertEqual(game.black.single._player.name, p1.name)
        self.assertEqual(game.white.single._player.name, p2.name)

        self.assertEqual(game.black.single._playto, game.playto)
        self.assertEqual(game.white.single._playto, game.playto)

    def test_get_name(self):
        p1 = Player()
        p1.set_name("P1")

        p2 = Player()
        p2.set_name("P2")

        game = Game() # Order is important
        game.black.set_player([p1])
        game.white.set_player([p2])

        self.assertEqual(game.black.single._player.name, p1.name)
        self.assertEqual(game.white.single._player.name, p2.name)

    def test_set_playto(self):
        p1 = Player()
        p1.set_name("P1")

        p2 = Player()
        p2.set_name("P2")

        game = Game() # Order is important
        game.black.set_player([p1])
        game.white.set_player([p2])
        game.set_playto(10)

        self.assertEqual(game.black.single._playto, 10)
        self.assertEqual(game.white.single._playto, 10)

    def test_add_and_del(self):
        p1 = Player()
        p1.set_name("P1")

        p2 = Player()
        p2.set_name("P2")

        game = Game() # Order is important
        game.black.set_player([p1])
        game.white.set_player([p2])

        playto = 6
        game.set_playto(playto)

        game.black.single.del_goal()
        game.black.single.del_owner()
        game.black.single.del_foul()

        self.assertEqual(game.black.single.goal, 0)
        self.assertEqual(game.black.single.own, 0)
        self.assertEqual(game.black.single.foul, 0)

        for i in range(1, 8):
            game.black.single.add_goal()
            game.black.single.add_owner()
            game.black.single.add_foul()

        self.assertEqual(game.black.single.goal, playto)
        self.assertEqual(game.black.single.own, playto)
        self.assertEqual(game.black.single.foul, i)