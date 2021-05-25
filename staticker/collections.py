from .core import Event, Player, get_player_by_id, get_player_by_name


class PlayerCollection:
    def __init__(self):
        self.player = []

    def load_all(self, sort_by=None):
        if sort_by is None:
            self.player = [p for p in Player.select()]
        elif sort_by == "name":
            self.player = [p for p in Player.select().order_by(Player.name)]

    def get_names(self):
        return [p.name for p in self.player]

    def get_player(self):
        return self.player


class EventCollection:
    def __init__(self):
        self.events = []

    def load_all(self):
        self.events = [ev for ev in Event.select()]

    def get_events(self):
        return self.events
