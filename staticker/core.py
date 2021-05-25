from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegerField, ForeignKeyField, BooleanField
from playhouse.sqlite_ext import JSONField
from datetime import datetime
from .folder import DBDirectory


dir = DBDirectory()
dir.mk_dir()
db = SqliteDatabase(str(dir.get_db_path()))


class BaseModel(Model):
    class Meta:
        database = db


#################################################################
#################################################################


class Event(BaseModel):
    mode = CharField()
    elements = JSONField(default={"p": [], "g": []})

    def add_player(self, player):
        for p in player:
            if p.id not in self.elements["p"]:
                self.elements["p"].append(p.id)

        self.save()

    def add_game(self, game):
        if self.mode == "free":
            existing_games = get_multiple_games_by_id(self.elements["g"])
            for g in existing_games:
                if not g.finished:
                    msg = (
                        "Attempted to add a new game, "
                        f"although game with id {g.id} "
                        "has not yet been finished."
                    )
                    raise(Exception(msg))

            for pid in game.get_player_ids():
                if pid not in self.elements["p"]:
                    msg = f"Player with id {pid} not in this event."
                    raise(Exception(msg))

            self.elements["g"].append(game.id)

        self.save()


#################################################################
#################################################################


class Player(BaseModel):
    name = CharField(unique=True)
    created = DateTimeField(default=datetime.now)

    def played_games(self):
        query = Game.select().where(
            (Game.player_b_def == self) |
            (Game.player_b_off == self) |
            (Game.player_w_def == self) |
            (Game.player_w_off == self)
        ).order_by(Game.id)
        return [p for p in query]


#################################################################
#################################################################


class Game(BaseModel):
    created = DateTimeField(default=datetime.now)
    mode = CharField(default="")
    playto = IntegerField(default=6)
    started = BooleanField(default=False)
    finished = BooleanField(default=False)
    history = CharField(default="")
    player_b_def = ForeignKeyField(Player, backref="b_def")
    player_b_off = ForeignKeyField(Player, backref="b_off")
    player_w_def = ForeignKeyField(Player, backref="w_def")
    player_w_off = ForeignKeyField(Player, backref="w_off")

    def add_player(self, black, white):
        assert type(black) == list
        assert type(white) == list
        assert any(p in white for p in black) == False

        mode = ""

        if len(black) == 1:
            self.player_b_def = black[0]
            self.player_b_off = black[0]
            mode += "1b"
        elif len(black) == 2:
            self.player_b_def = black[0]
            self.player_b_off = black[1]
            mode += "2b"
        else:
            msg = "Length of black must equals 1 or 2"
            raise(Exception(msg))

        mode += "_"

        if len(white) == 1:
            self.player_w_def = white[0]
            self.player_w_off = white[0]
            mode += "1w"
        elif len(white) == 2:
            self.player_w_def = white[0]
            self.player_w_off = white[1]
            mode += "2w"
        else:
            msg = "Length of white must equals 1 or 2"
            raise(Exception(msg))

        self.mode = mode
        self.save()

    def goal(self, side, slot):
        if self.finished:
            raise(Exception("Game is already finished."))
        if side == "b" and slot == "def":
            msg = "gbd"
        elif side == "b" and slot == "off":
            msg = "gbo"
        elif side == "w" and slot == "def":
            msg = "gwd"
        elif side == "w" and slot == "off":
            msg = "gwo"
        self.add_to_history(msg)

    def owner(self, side, slot):
        if self.finished:
            raise(Exception("Game is already finished."))
        if side == "b" and slot == "def":
            msg = "obd"
        elif side == "b" and slot == "off":
            msg = "obo"
        elif side == "w" and slot == "def":
            msg = "owd"
        elif side == "w" and slot == "off":
            msg = "owo"
        self.add_to_history(msg)

    def decode(self):
        msgs = self.history.split("_")
        counters = {
            "gbd": 0,
            "gbo": 0,
            "gwd": 0,
            "gwo": 0,
            "obd": 0,
            "obo": 0,
            "owd": 0,
            "owo": 0
        }
        for msg in msgs:
            if msg == "":
                continue
            counters[msg] += 1
        return counters

    def add_to_history(self, msg):
        sep = "_" if self.history else ""
        self.history += sep + msg
        self.update_fields_and_save()

    def undo(self):
        msgs = self.history.split("_")
        msgs = msgs[:-1]
        self.history = "_".join(msgs)
        self.update_fields_and_save()

    def get_score(self):
        counters = self.decode()
        gb = counters["gbd"] + counters["gbo"]
        gw = counters["gwd"] + counters["gwo"]
        ob = counters["obd"] + counters["obo"]
        ow = counters["owd"] + counters["owo"]

        return {"b": gb + ow, "w": gw + ob}

    def update_fields_and_save(self):
        score = self.get_score()
        self.started = bool(self.history)
        self.finished = score["b"] >= self.playto or score["w"] >= self.playto
        self.save()

    def switch_sides(self):
        if self.started:
            raise(Exception("Unable to switch sides, game has already started."))

        pbd = self.player_b_def
        pbo = self.player_b_off
        pwd = self.player_w_def
        pwo = self.player_w_off

        self.player_b_def = pwd
        self.player_b_off = pwo
        self.player_w_def = pbd
        self.player_w_off = pbo

        self.save()

    def switch_slots(self, side):
        if self.started:
            raise(Exception("Unable to switch slots, game has already started."))

        pbd = self.player_b_def
        pbo = self.player_b_off
        pwd = self.player_w_def
        pwo = self.player_w_off

        if side == "b":
            self.player_b_def = pbo
            self.player_b_off = pbd
        elif side == "w":
            self.player_w_def = pwo
            self.player_w_off = pwd

        self.save()

    def get_player_ids(self):
        bd = self.player_b_def.id
        bo = self.player_b_off.id
        wd = self.player_w_def.id
        wo = self.player_w_off.id

        return tuple(set((bd, bo, wd, wo)))


db.create_tables([Player, Game, Event])


#################################################################
#################################################################


def get_game_by_id(game_id):
    try:
        return Game[game_id]
    except:
        raise(Exception(f"No game with id {game_id} found."))


def get_multiple_games_by_id(game_ids):
    try:
        return [g for g in Game.select().where(Game.id << game_ids)]
    except:
        raise(Exception(f"No games with given ID's found."))

###############################


def get_player_by_id(player_id):
    try:
        return Player[player_id]
    except:
        raise(Exception(f"No player with id {player_id} found."))


def get_multiple_player_by_id(player_ids):
    try:
        return [p for p in Player.select().where(Player.id << player_ids)]
    except:
        raise(Exception(f"No player with given ID's found."))


def get_player_by_name(player_name):
    try:
        return Player.select().where(Player.name == player_name).get()
    except:
        raise(Exception(f"No player with name {player_name} found."))


def get_multiple_player_by_name(player_names):
    try:
        return [p for p in Player.select().where(Player.name << player_names)]
    except:
        raise(Exception(f"No players with given names found."))


###############################

def get_event_by_id(event_id):
    try:
        return Event[event_id]
    except:
        raise(Exception(f"No event with id {event_id} found."))


def get_multiple_events_by_id(event_ids):
    try:
        return [ev for ev in Event.select().where(Event.id << event_ids)]
    except:
        raise(Exception(f"No events with given ID's found."))
