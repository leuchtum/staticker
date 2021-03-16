from pydantic import BaseModel, PrivateAttr
from .player import Player
from .time import Time
from .database import SingleBase, Handler

#################################################
#################################################

class Slot(BaseModel):
    goal: int = 0
    own: int = 0
    foul: int = 0
    id: str = None
    _playto: int = PrivateAttr(default=0)
    _player: Player = PrivateAttr()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self, **data):
        super().__init__(**data)
        if self.id:
            self._player = Player()
            self._player.load(self.id)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_goals(self):
        return self.goal
#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_owners(self):
        return self.own
#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_fouls(self):
        return self.foul
#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_name(self):
        return self._player.name

#–––––––––––––––––––––––––––––––––––––––––––––––– 

    def set_playto(self, playto: int):
        self._playto = playto

#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_player(self, player):
        self.id = player.id
        self._player = player

#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_goal(self):
        if self.goal < self._playto:
            self.goal += 1

#––––––––––––––––––––––––––––––––––––––––––––––––

    def del_goal(self):
        if self.goal > 0:
            self.goal -= 1

#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_owner(self):
        if self.own < self._playto:
            self.own += 1

#––––––––––––––––––––––––––––––––––––––––––––––––

    def del_owner(self):
        if self.own > 0:
            self.own -= 1

#––––––––––––––––––––––––––––––––––––––––––––––––

    def add_foul(self):
        self.foul += 1

#––––––––––––––––––––––––––––––––––––––––––––––––

    def del_foul(self):
        if self.foul > 0:
            self.foul -= 1

#################################################
#################################################

class Side(BaseModel):
    single: Slot = None
    defense: Slot = None
    offense: Slot = None
    _mode: str = PrivateAttr(default=None)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self, **data):
        super().__init__(**data)
        self._set_mode()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def _set_mode(self):
        if self.single:
            self._mode = "single"
        elif self.defense and self.offense:
            self._mode = "multi"

#––––––––––––––––––––––––––––––––––––––––––––––––

    def set_player(self, player: list):
        if len(player) == 1:
            self.single = Slot()
            self.defense = None
            self.offense = None
            self.single.add_player(player[0])

        elif len(player) == 2:
            self.single = None
            self.defense = Slot()
            self.offense = Slot()
            self.defense.add_player(player[0])
            self.offense.add_player(player[1])

        self._set_mode()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def set_playto(self, playto):
        if self.single:
            self.single.set_playto(playto)
        if self.defense:
            self.defense.set_playto(playto)
        if self.offense:
            self.offense.set_playto(playto)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_goals(self):
        if self._mode == "single":
            goal = self.single.goal
        elif self._mode == "multi":
            goal = self.offense.goal + self.defense.goal
        return goal
    
#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_owners(self):
        if self._mode == "single":
            owner = self.single.own
        elif self._mode == "multi":
            owner = self.offense.own + self.defense.own
        return owner

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_fouls(self):
        if self._mode == "single":
            foul = self.single.foul
        elif self._mode == "multi":
            foul = self.offense.foul + self.defense.foul
        return foul

#––––––––––––––––––––––––––––––––––––––––––––––––

    def flip_slots(self):
        store = self.offense
        self.offense = self.defense
        self.defense = store

#################################################
#################################################

class Game(BaseModel, SingleBase):
    id: str = None
    time: Time = None
    black: Side = None
    white: Side = None
    playto: int = 6
    _tablename: str = PrivateAttr(default="game")

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = Handler().new_key()

        if not self.time:
            self.time = Time()
        if not self.black:
            self.black = Side()
        if not self.white:
            self.white = Side()

        if self.playto:
            self.set_playto(self.playto)
        
#––––––––––––––––––––––––––––––––––––––––––––––––

    def set_playto(self, playto):
        self.playto = playto
        self.black.set_playto(playto)
        self.white.set_playto(playto)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_playto(self):
        return self.playto

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_score(self):
        goal = self.black.get_goals()
        own = self.white.get_owners()
        score_black = goal + own

        goal = self.white.get_goals()
        own = self.black.get_owners()
        score_white = goal + own

        return {
            "score_black": score_black,
            "score_white": score_white
        }

#––––––––––––––––––––––––––––––––––––––––––––––––

    def is_finished(self):
        goal = self.black.get_goals()
        own = self.white.get_owners()
        score_black = goal + own

        goal = self.white.get_goals()
        own = self.black.get_owners()
        score_white = goal + own

        finished = False
        if max([score_black, score_white]) >= self.playto:
            finished = True
        return finished

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_slot_by_id(self, player_id):
        side = self.get_side_by_id(player_id)
        if side.single and side.single.id == player_id:
            return side.single
        if side.defense and side.defense.id == player_id:
            return side.defense
        if side.offense and side.offense.id == player_id:
            return side.offense

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_side_by_id(self, player_id):
        if self.black.single and self.black.single.id == player_id:
            return self.black
        if self.black.defense and self.black.defense.id == player_id:
            return self.black
        if self.black.offense and self.black.offense.id == player_id:
            return self.black

        if self.white.single and self.white.single.id == player_id:
            return self.white
        if self.white.defense and self.white.defense.id == player_id:
            return self.white
        if self.white.offense and self.white.offense.id == player_id:
            return self.white

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_position_result(self, player_id):
        side = self.get_side_by_id(player_id)

        if side == self.black:
            opp_side = self.white
        if side == self.white:
            opp_side = self.black

        mode = ""

        if side._mode == "single" and opp_side._mode == "single":
            mode = "1vs1"
        elif side._mode == "single" and opp_side._mode == "multi":
            mode = "Svs2"
        elif side._mode == "multi" and opp_side._mode == "single":
            mode = "Tvs1"
        elif side._mode == "multi" and opp_side._mode == "multi":
            mode = "2vs2"

        partner = None
        position = None

        if side._mode == "multi":
            if side.defense.id == player_id:
                partner = side.offense.id
                position = "DEF"
            else:
                partner = side.defense.id
                position = "OFF"

        opponents = []
        if opp_side._mode == "single":
            opponents.append(opp_side.single.id)
        else:
            opponents.append(opp_side.defense.id)
            opponents.append(opp_side.offense.id)

        slot = self.get_slot_by_id(player_id)
        goals_slot = slot.goal
        owners = slot.owner
        fouls = slot.foul

        goals_side = side.get_goals()
        goals_opp_side = opp_side.get_goals()

        won = goals_side >= self.playto
        lost = goals_opp_side >= self.playto
        lost_to_zero = goals_side == 0

        return {
            "game_id": self.id,
            "mode": mode,
            "duration": self.time.get_duration(),
            "side": side._color,
            "position": position,
            "won": won,
            "lost": lost,
            "lost_to_zero": lost_to_zero,
            "goals_side": goals_side,
            "goals_slot": goals_slot,
            "goals_opp_side": goals_opp_side,
            "owners": owners,
            "fouls": fouls,
            "partner": partner,
            "opponents": opponents
        }

#––––––––––––––––––––––––––––––––––––––––––––––––

    def flip_sides(self):
        store = self.black
        self.black = self.white
        self.white = store