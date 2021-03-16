from .collection import GameCollection
from .player import Player

#################################################
#################################################

class SetStat:

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self):
        self.played = 0

        self.won = 0
        self.lost = 0
        self.lost_to_0 = 0

        self.goals_slot = 0
        self.goals_side = 0
        self.goals_opp_side = 0
        
        self.owners = 0
        self.fouls = 0

        self.position_owners = {}
        self.position_goals = {}
        self.position_played = {}
        self.partner = {}
        self.opponents = {}

        self.percent_won = None
        self.percent_lost = None
        self.percent_lost_to_0 = None

#––––––––––––––––––––––––––––––––––––––––––––––––

    def add(self, stat):
        self.played += 1

        self.won += stat["won"]
        self.lost += stat["lost"]
        self.lost_to_0 += stat["lost_to_0"]

        self.goals_slot += stat["goals_slot"]
        self.goals_side += stat["goals_side"]
        self.goals_opp_side += stat["goals_opp_side"]
        
        self.owners += stat["owners"]
        self.fouls += stat["fouls"]


        self.recount_dic(self.position_goals, stat["position_goals"])
        self.recount_dic(self.position_owners, stat["position_owners"])
        self.recount_list(self.position_played, stat["position_played"])
        self.recount_list(self.partner, stat["partner"])
        self.recount_list(self.opponents, stat["opponents"])

        self.update()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def recount_dic(self, self_obj, dic):
        for key, val in dic.items():
            if key in self_obj:
                self_obj[key] += val
            else:
                self_obj[key] = val
#––––––––––––––––––––––––––––––––––––––––––––––––

    def recount_list(self, self_obj, keys):
        for key in keys:
            if key in self_obj:
                self_obj[key] += 1
            else:
                self_obj[key] = 1

#––––––––––––––––––––––––––––––––––––––––––––––––

    def update(self):
        if self.played:
            self.percent_won = self.won / self.played
            self.percent_lost = self.lost / self.played
            self.percent_lost_to_0 = self.lost_to_0 / self.played

#################################################
#################################################

class PlayerStat:

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self, player, session=None, glob=False):
        if type(player) != Player:
            raise(TypeError)

        self.player = player
        self.collection = GameCollection()
        self.collection.load(player.games)

        self.session = SetStat()
        self.glob_all = SetStat()
        self.glob_2vs2 = SetStat()
        self.glob_1vs1 = SetStat()
        self.glob_Tvs1 = SetStat()
        self.glob_Svs2 = SetStat()

        for game in self.collection.get_objects():
            slot, side, opp_side = self.make_side_and_slot(game)
            mode = self.make_mode(side, opp_side)
            playto = game.playto

            stat = {}
            stat.update(self.make_partner(side))
            stat.update(self.make_opponents(opp_side))
            stat.update(self.make_position_goals(slot, side))
            stat.update(self.make_position_owners(slot, side))
            stat.update(self.make_position_played(slot, side))
            stat.update(self.make_goals_and_result(playto, slot, side, opp_side))
            if session:
                self.session.add(stat)
            if glob:
                self.glob_all.add(stat)
                if mode == "2vs2":
                    self.glob_2vs2.add(stat)
                if mode == "1vs1":
                    self.glob_1vs1.add(stat)
                if mode == "Tvs1":
                    self.glob_Tvs1.add(stat)
                if mode == "Svs2":
                    self.glob_Svs2.add(stat)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def make_side_and_slot(self, game):
        side = game.get_side_by_id(self.player.id)
        slot = game.get_slot_by_id(self.player.id)

        if side == game.black:
            opp_side = game.white
        if side == game.white:
            opp_side = game.black
        return slot, side, opp_side

#––––––––––––––––––––––––––––––––––––––––––––––––

    def make_mode(self, side, opp_side):
        mode = ""
        if side._mode == "single" and opp_side._mode == "single":
            mode = "1vs1"
        elif side._mode == "single" and opp_side._mode == "multi":
            mode = "Svs2"
        elif side._mode == "multi" and opp_side._mode == "single":
            mode = "Tvs1"
        elif side._mode == "multi" and opp_side._mode == "multi":
            mode = "2vs2"
        return {"mode": mode}

#––––––––––––––––––––––––––––––––––––––––––––––––

    def make_partner(self, side):
        partner = []
        if side._mode == "multi":
            if side.defense.id == self.player.id:
                partner.append(side.offense.id)
            else:
                partner.append(side.defense.id)
        return {"partner": partner}

#––––––––––––––––––––––––––––––––––––––––––––––––

    def make_opponents(self, opp_side):
        opponents = []
        if opp_side._mode == "single":
            opponents.append(opp_side.single.id)
        else:
            opponents.append(opp_side.defense.id)
            opponents.append(opp_side.offense.id)
        return {"opponents": opponents}

#––––––––––––––––––––––––––––––––––––––––––––––––

    def make_position_played(self, slot, side):
        position = "SINGLE"
        if side._mode == "multi":
            position = "DEF" if side.defense.id == self.player.id else "OFF"
        return {"position_played": [position]}
#––––––––––––––––––––––––––––––––––––––––––––––––

    def make_position_owners(self, slot, side):
        owner = slot.get_owners()
        position = "SINGLE"
        if side._mode == "multi":
            position = "DEF" if side.defense.id == self.player.id else "OFF"
        return {"position_owners": {position: owner}}
        
#––––––––––––––––––––––––––––––––––––––––––––––––

    def make_position_goals(self, slot, side):
        goal = slot.get_goals()
        position = "SINGLE"
        if side._mode == "multi":
            position = "DEF" if side.defense.id == self.player.id else "OFF"
        return {"position_goals": {position: goal}}
#––––––––––––––––––––––––––––––––––––––––––––––––

    def make_goals_and_result(self, playto, slot, side, opp_side):
        
        goals_slot = slot.get_goals()
        owners = slot.get_owners()
        fouls = slot.get_fouls()

        goals_side = side.get_goals()
        goals_opp_side = opp_side.get_goals()

        owners_side = side.get_owners()
        owners_opp_side = opp_side.get_owners()

        won = goals_side + owners_opp_side >= playto
        lost = goals_opp_side + owners_side >= playto
        lost_to_0 = goals_side == 0

        return {
            "won": won,
            "lost": lost,
            "lost_to_0": lost_to_0,
            "goals_side": goals_side,
            "goals_slot": goals_slot,
            "goals_opp_side": goals_opp_side,
            "owners": owners,
            "fouls": fouls,
        }
        