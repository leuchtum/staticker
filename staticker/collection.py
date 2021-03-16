from .game import Game
from .player import Player
from .database import MultiBase

#################################################
#################################################

class PlayerCollection(MultiBase):
    _tablename = "player"
    _class = Player

#################################################
#################################################

class GameCollection(MultiBase):
    _tablename = "game"
    _class = Game