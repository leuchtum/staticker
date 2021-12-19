from .collections import PlayerCollection, GameCollection
import pandas as pd
import numpy as np
from .core import NotAllowedError


class GlobalStatistics:
    def __init__(self):
        self.pc = PlayerCollection()
        self.pc.load_all()
        self.gc = GameCollection()
        self.gc.load_all()

        self.stats = {
            p: {
                "total": 0,
                "won": 0,
                "lost": 0,
                "won%": 0,
                "lost%": 0,
                "shot": 0,
                "shot_from_defense": 0,
                "shot_from_offense": 0,
                "owner": 0,
                "shot%": 0,
                "shot_from_defense%": 0,
                "shot_from_offense%": 0,
                "owner%": 0,
            }
            for p in self.pc.player
        }

        self.make_total()
        self.make_won_lost()
        self.make_shot_owner()
        self.make_relativ()

    def make_total(self):
        for game in self.gc.games:
            if game.finished:
                for p in game.get_player():
                    self.stats[p]["total"] += 1

    def make_won_lost(self):
        for game in self.gc.games:
            if game.finished:
                wandl = game.get_winner_and_loser()
                for p in wandl["winner"]:
                    self.stats[p]["won"] += 1
                for p in wandl["loser"]:
                    self.stats[p]["lost"] += 1

    def make_shot_owner(self):
        for game in self.gc.games:
            if game.id == 70:
                print("")
            if game.finished:
                for p in game.get_player():
                    history = game.get_player_history(p)
                    for key in history:
                        if key[0] == "g":
                            self.stats[p]["shot"] += 1
                            if key[2] == "d":
                                self.stats[p]["shot_from_defense"] += 1
                            else:
                                self.stats[p]["shot_from_offense"] += 1
                        elif key[0] == "o":
                            self.stats[p]["owner"] += 1
                        else:
                            raise (ValueError)

    def make_relativ(self):
        for s in self.stats.values():
            if s["total"] == 0:
                s["lost%"] = 100
            else:
                s["won%"] = s["won"] / s["total"] * 100
                s["lost%"] = s["lost"] / s["total"] * 100

                s["shot%"] = s["shot"] / s["total"]
                s["shot_from_defense%"] = s["shot_from_defense"] / s["total"]
                s["shot_from_offense%"] = s["shot_from_offense"] / s["total"]
                s["owner%"] = s["owner"] / s["total"]

    def get_formatted_stats(self):
        return_list = []
        for p, s in self.stats.items():

            for key, val in s.items():
                if "%" in key:
                    s[key] = round(val, 3)

            s.update({"name": p.name})
            return_list.append(s)
        return return_list


class EventStatistics:
    def __init__(self, event):
        self.event = event

        self.pc = PlayerCollection()
        self.pc.player = self.event.get_player()

        self.gc = GameCollection()
        self.gc.games = self.event.get_games(finished=True)

        self.ranking = pd.DataFrame(
            data=[
                {"player": p, "name": p.name, "name_lower_case": p.name.lower()}
                for p in self.pc.player
            ],
            index=[p.id for p in self.pc.player],
        )

    def games_played(self):
        return len(self.event.get_games(finished=True))

    def _count(self):
        metrics_names = ["played", "won", "lost"]

        zeros = np.zeros((self.ranking.shape[0], len(metrics_names)), dtype=int)
        metrics = pd.DataFrame(
            data=zeros, columns=metrics_names, index=self.ranking.index
        )

        self.ranking = self.ranking.join(metrics)

        for g in self.gc.games:
            wl = g.get_winner_and_loser()
            for p in g.get_player():
                if p in wl["winner"]:
                    self.ranking.loc[p.id, "played"] += 1
                    self.ranking.loc[p.id, "won"] += 1
                elif p in wl["loser"]:
                    self.ranking.loc[p.id, "played"] += 1
                    self.ranking.loc[p.id, "lost"] += 1

    def get_main_ranking(self):
        self._count()

        main_info = ["ranking", "name", "played", "won", "lost"]
        sort_by = ["won", "lost", "played", "name_lower_case"]
        ascending = [False, True, False, True]

        ranking = self.ranking.sort_values(sort_by, ascending=ascending)
        ranking["ranking"] = range(1, len(ranking) + 1)

        return ranking[main_info].to_dict(orient="records")
