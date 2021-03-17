from pydantic import BaseModel, PrivateAttr
from .database import Handler, SingleBase
from .player import Player
from .game import Game
from .time import Time
from typing import List

#################################################
#################################################

class Session(BaseModel, SingleBase):
    id: str = None
    game_ids: List[str] = []
    player_ids: List[str] = []
    time: Time = None
    playto: int = 6
    mode: str = None
    _tablename: str = PrivateAttr(default="session")
    _settings = PrivateAttr(default=None)
    _players = PrivateAttr(default=[])
    _games = PrivateAttr(default=[])

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = Handler().new_key()
        if not self.time:
            self.time = Time()
        self._load_objs()
        self._set_settings()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def _load_objs(self):
        for pid in self.player_ids:
            p = Player()
            p.load(pid)
            self._players.append(p)
            
        for gid in self.game_ids:
            g = Game()
            g.load(gid)
            self._games.append(g)
            
#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_players(self, players: list):
        if type(players) != list:
            raise(TypeError)
        for p in players:
            if p.id not in self.player_ids:
                self.player_ids.append(p.id)
            if p not in self._players:
                self._players.append(p)
                
#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_games(self, games: list):
        if type(games) != list:
            raise(TypeError)
        for g in games:
            if g.id not in self.game_ids:
                self.game_ids.append(g.id)
            if g not in self._games:
                self._games.append(g)
                
#––––––––––––––––––––––––––––––––––––––––––––––––

    def set_playto(self, playto: int):
        if type(playto) != int:
            raise(TypeError)
        self.playto = playto
        for g in self._games:
            g.set_playto(self.playto)
      
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