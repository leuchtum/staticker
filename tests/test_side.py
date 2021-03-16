import unittest
from staticker.player import Player
from staticker.game import Game, Slot, Side

class SidePlayer(unittest.TestCase):

    def setUp(self):
        self.side = Side()

    def test_init(self):
        self.assertIs(self.side._mode , None)
        self.assertIs(self.side.single , None)
        self.assertIs(self.side.defense , None)
        self.assertIs(self.side.offense , None)

    def test_set_player(self):
        p1 = Player()
        p1.set_name("P1")

        p2 = Player()
        p2.set_name("P2")

        p3 = Player()
        p3.set_name("P3")

        game = Game() # Order is important
        game.black.set_player([p1])
        game.white.set_player([p2, p3])

        self.assertIs(type(game.black.single), Slot)
        self.assertIs(game.black.defense, None)
        self.assertIs(game.black.offense, None)

        self.assertIs(game.white.single, None)
        self.assertIs(type(game.white.defense), Slot)
        self.assertIs(type(game.white.offense), Slot)

        self.assertIs(game.black._mode, "single")
        self.assertIs(game.white._mode, "multi")

    def test_set_playto(self):
        p1 = Player()
        p1.set_name("P1")

        p2 = Player()
        p2.set_name("P2")

        p3 = Player()
        p3.set_name("P3")

        game = Game() # Order is important
        game.black.set_player([p1])
        game.white.set_player([p2, p3])

        playto = 10
        game.set_playto(playto)

        self.assertEqual(game.black.single._playto, playto)
        self.assertEqual(game.white.defense._playto, playto)
        self.assertEqual(game.white.offense._playto, playto)

    def test_get_goals_owners_fouls(self):
        p1 = Player()
        p1.set_name("P1")

        p2 = Player()
        p2.set_name("P2")

        p3 = Player()
        p3.set_name("P3")

        game = Game() # Order is important
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

        self.assertEqual(game.black.get_goals(), 1)
        self.assertEqual(game.black.get_owners(), 1)
        self.assertEqual(game.black.get_fouls(), 1)

        self.assertEqual(game.white.get_goals(), 2)
        self.assertEqual(game.white.get_owners(), 2)
        self.assertEqual(game.white.get_fouls(), 2)

    def test_flip_slots(self):
        p1 = Player()
        p1.set_name("P1")

        p2 = Player()
        p2.set_name("P2")

        p3 = Player()
        p3.set_name("P3")

        game = Game() # Order is important
        game.black.set_player([p1])
        game.white.set_player([p2, p3])

        slot1 = game.white.defense
        slot2 = game.white.offense

        game.white.flip_slots()

        self.assertIs(game.white.defense, slot2)
        self.assertIs(game.white.offense, slot1)