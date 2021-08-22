from .core import Event
from .collections import PlayerCollection, GameCollection
import pandas as pd
import numpy as np


class EventStatistics():
    def __init__(self, event):
        self.event = event

        self.pc = PlayerCollection()
        self.pc.player = self.event.get_player()

        self.gc = GameCollection()
        self.gc.games = self.event.get_games(finished=True)

        self.ranking = pd.DataFrame(
            data=[{"player": p, "name": p.name, "name_lower_case": p.name.lower()}
                  for p in self.pc.player],
            index=[p.id for p in self.pc.player]
        )

    def games_played(self):
        return len(self.event.get_games(finished=True))

    def _count(self):
        metrics_names = ["played", "won", "lost"]

        zeros = np.zeros(
            (self.ranking.shape[0], len(metrics_names)), dtype=int)
        metrics = pd.DataFrame(
            data=zeros, columns=metrics_names, index=self.ranking.index)

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
