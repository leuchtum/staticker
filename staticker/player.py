from pydantic import BaseModel, PrivateAttr
from .database import Handler, SingleBase
from typing import List

###############################################
#################################################

class Player(BaseModel, SingleBase):
    id: str = None
    name: str = None
    games: List[str] = []
    _tablename: str = PrivateAttr(default="player")

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = Handler().new_key()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def set_name(self, name: str):
        if type(name) != str:
            raise(TypeError)
        self.name = name

#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_game(self, game_id: str):
        if type(game_id) != str:
            raise(TypeError)
        self.games.append(game_id)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def del_game(self, game_id: str):
        if type(game_id) != str:
            raise(TypeError)
        for i in range(len(self.games)):
            if game_id == self.games[i]:
                self.games.pop(i)
                break