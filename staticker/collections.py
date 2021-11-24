from .core import Event, Player, get_player_by_id, get_player_by_name
from peewee import fn


class PlayerCollection:
    def __init__(self):
        self.player = []

    def load_all(self, sort_by=None):
        self.player = [p for p in Player.select()]
        if sort_by:
            self.player = self.get_sorted(sort_by)

    def get_sorted(self, sort_by):
        self.player.sort(key=lambda p: p.name.lower())
        return self.player

    def get_names(self):
        return [p.name for p in self.player]

    def get_player(self):
        return self.player

    def get_names_with_ids(self):
        return {p.name: p.id for p in self.player}


class GameCollection:
    def __init__(self):
        self.games = []

    def get_formatted_games(self):
        formatted_games = []
        for g in self.games:
            score = g.get_score()
            entry = {
                "pwd": g.pwd.name,
                "pwo": g.pwo.name,
                "pbd": g.pbd.name,
                "pbo": g.pbo.name,
                "score_w": score["w"],
                "score_b": score["b"],
                "created": g.created,
            }
            formatted_games.append(entry)

        formatted_games.sort(key=lambda x: x["created"])
        return formatted_games


class EventCollection:
    def __init__(self):
        self.events = []

    def load_all(self):
        self.events = [ev for ev in Event.select()]

    def get_events(self):
        return self.events
