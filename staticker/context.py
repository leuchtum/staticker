from .player import Player
from .collection import PlayerCollection

class Context():
    def __init__(self) -> None:
        self.active_session = None
    
    def get_player(self, player_id: str):
        p = Player()
        try:
            p.load(player_id)
            return p
        except:
            return None
        
    def get_players(self, all=False):
        if all:
            pc = PlayerCollection()
            pc.load_all()
            pc.sort()
            return pc.get_objects()
        
    def name_exists(self, name: str):
        pc = PlayerCollection()
        pc.load_all()
        names = [p.name for p in pc.get_objects()]
        return name in names
    
    def new_player(self, name: str):
        p = Player()
        p.set_name(name)
        p.dump()
        return p