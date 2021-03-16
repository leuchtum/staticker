from pydantic import BaseModel, PrivateAttr
from .database import Handler, SingleBase
from .player import Player
from .time import Time
from typing import List

#################################################
#################################################

class Session(BaseModel, SingleBase):
    id: str = None
    games: List[str] = []
    players: List[str] = []
    time: Time = None
    playto: int = 6
    mode: str = None
    _tablename: str = PrivateAttr(default="session")
    _settings = PrivateAttr(default=None)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = Handler().new_key()
        if not self.time:
            self.time = Time()
        self._set_settings()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_players(self, players: list):
        if type(players) != list:
            raise(TypeError)
        for p in players:
            if p.id not in self.players:
                self.players.append(p.id)
                
#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_games(self, games: list):
        if type(games) != list:
            raise(TypeError)
        for g in games:
            if g.id not in self.games:
                self.games.append(g.id)
                
#––––––––––––––––––––––––––––––––––––––––––––––––

    def set_playto(self, playto: int):
        if type(playto) != int:
            raise(TypeError)
        self.playto = playto
      
#––––––––––––––––––––––––––––––––––––––––––––––––

    def set_mode(self, mode: int):
        if type(mode) != str:
            raise(TypeError)
        if mode == "free":
            self.mode = "free"
        else:
            raise(ValueError)
        self._set_settings()
                  
#––––––––––––––––––––––––––––––––––––––––––––––––

    def _set_settings(self):
        if self.mode == "free":
            self._settings = {}
                 
#################################################
#################################################