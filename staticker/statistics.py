from .collections import PlayerCollection, GameCollection
import pandas as pd
import numpy as np
from .core import NotAllowedError


class Statistics:
    def __init__(self):
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
            for p in game.get_player():
                self.stats[p]["total"] += 1

    def make_won_lost(self):
        for game in self.gc.games:
            wandl = game.get_winner_and_loser()
            for p in wandl["winner"]:
                self.stats[p]["won"] += 1
            for p in wandl["loser"]:
                self.stats[p]["lost"] += 1

    def make_shot_owner(self):
        for game in self.gc.games:
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


class GlobalStatistics(Statistics):
    def __init__(self):
        self.pc = PlayerCollection()
        self.pc.load_all()
        self.gc = GameCollection()
        self.gc.load_all(only_finished_games=True)
        super().__init__()


class EventStatistics(Statistics):
    def __init__(self, event):
        self.pc = PlayerCollection()
        self.pc.load_from_event(event)
        self.gc = GameCollection()
        self.gc.load_from_event(event, only_finished_games=True)
        super().__init__()

    def get_main_ranking(self):
        ranking = pd.DataFrame.from_records(self.get_formatted_stats())
        ranking["name_lower_case"] = ranking["name"].apply(str.lower)

        sort_by = ["won", "lost", "total", "name_lower_case"]
        ascending = [False, True, False, True]
        ranking = ranking.sort_values(sort_by, ascending=ascending)

        ranking["ranking"] = range(1, len(ranking) + 1)

        main_info = ["ranking", "name", "total", "won", "lost"]
        return ranking[main_info].to_dict(orient="records")


class PlayerStatistics:
    def __init__(self, player):
        self.player = player

        self.gc = GameCollection()
        self.gc.load_from_player(player)

        self.stats = {
            "total": len(self.gc.games),
            "won": 0,
            "lost": 0,
            "played_w": 0,
            "played_b": 0,
            "played_allone": 0,
            "played_defense": 0,
            "played_offense": 0,
            "shot_defense": 0,
            "shot_offense": 0,
            "owner_defense": 0,
            "owner_offense": 0,
            "won%": 0,
            "lost%": 0,
            "played_w%": 0,
            "played_b%": 0,
            "played_allone%": 0,
            "played_defense%": 0,
            "played_offense%": 0,
            "shot_defense%": 0,
            "shot_offense%": 0,
            "owner_defense%": 0,
            "owner_offense%": 0,
        }

        self.make_won_lost()
        self.make_side()
        self.make_allone_defense_offense()
        self.make_shot_owner()
        self.make_relativ()

    def make_won_lost(self):
        for game in self.gc.games:
            side = game.get_side_by_player(self.player)
            other_side = "w" if side == "b" else "b"
            score = game.get_score()
            if score[side] > score[other_side]:
                self.stats["won"] += 1
            else:
                self.stats["lost"] += 1

    def make_side(self):
        for game in self.gc.games:
            side = game.get_side_by_player(self.player)
            if side == "w":
                self.stats["played_w"] += 1
            else:
                self.stats["played_b"] += 1

    def make_allone_defense_offense(self):
        for game in self.gc.games:
            mode = game.get_mode_by_player(self.player)
            if mode == "s":
                self.stats["played_allone"] += 1
            else:
                pos = game.get_position_by_player(self.player)
                if pos == "d":
                    self.stats["played_defense"] += 1
                else:
                    self.stats["played_offense"] += 1

    def make_shot_owner(self):
        for game in self.gc.games:
            history = game.get_player_history(self.player)
            for key in history:
                if key[0] == "g":
                    if key[2] == "d":
                        self.stats["shot_defense"] += 1
                    else:
                        self.stats["shot_offense"] += 1
                else:
                    if key[2] == "d":
                        self.stats["owner_defense"] += 1
                    else:
                        self.stats["owner_offense"] += 1

    def make_relativ(self):
        if self.stats["total"] == 0:
            self.stats["won%"] = 50
            self.stats["lost%"] = 50
            self.stats["played_w%"] = 50
            self.stats["played_b%"] = 50
            self.stats["played_allone%"] = 50
            self.stats["played_defense%"] = 50
            self.stats["played_offense%"] = 50
            self.stats["shot_defense%"] = 50
            self.stats["shot_offense%"] = 50
            self.stats["owner_defense%"] = 50
            self.stats["owner_offense%"] = 50
        else:
            self.stats["won%"] = round(self.stats["won"] / self.stats["total"], 2) * 100
            self.stats["lost%"] = (
                round(self.stats["lost"] / self.stats["total"], 2) * 100
            )
            self.stats["played_w%"] = (
                round(self.stats["played_w"] / self.stats["total"], 2) * 100
            )
            self.stats["played_b%"] = (
                round(self.stats["played_b"] / self.stats["total"], 2) * 100
            )
            self.stats["played_allone%"] = (
                round(self.stats["played_allone"] / self.stats["total"], 2) * 100
            )
            self.stats["played_defense%"] = (
                round(self.stats["played_defense"] / self.stats["total"], 2) * 100
            )
            self.stats["played_offense%"] = (
                round(self.stats["played_offense"] / self.stats["total"], 2) * 100
            )
            self.stats["shot_defense%"] = (
                round(self.stats["shot_defense"] / self.stats["total"], 2) * 100
            )
            self.stats["shot_offense%"] = (
                round(self.stats["shot_offense"] / self.stats["total"], 2) * 100
            )
            self.stats["owner_defense%"] = (
                round(self.stats["owner_defense"] / self.stats["total"], 2) * 100
            )
            self.stats["owner_offense%"] = (
                round(self.stats["owner_offense"] / self.stats["total"], 2) * 100
            )

    def get_formatted_stats(self):
        return self.stats
