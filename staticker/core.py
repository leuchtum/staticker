from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegerField, ForeignKeyField, BooleanField
from playhouse.sqlite_ext import JSONField
from datetime import datetime
from .folder import DBDirectory
from .log import logger


dir = DBDirectory()
dir.mk_dir()
db = SqliteDatabase(str(dir.get_db_path()))

#################################################################
#################################################################

class NotAllowedError(Exception):
    pass

class FatalError(Exception):
    pass

class NotFoundError(Exception):
    pass


#################################################################
#################################################################


class BaseModel(Model):
    class Meta:
        database = db


#################################################################
#################################################################


class Event(BaseModel): # TODO Rewrite JsonField? Games now have parent Event ID
    created = DateTimeField(default=datetime.now)
    mode = CharField()
    elements = JSONField(default={"p": [], "g": []})
    active = BooleanField(default=False)

    def add_player(self, player):
        if self._is_active():
            for p in player:
                if p.id not in self.elements["p"]:
                    self.elements["p"].append(p.id)

            self.save()
            logger.debug(f"Player {player} were added to Event[{self}].")

    def add_game(self, game):
        if not game.id:
            msg = (
                "Game has no ID and cannot be added to event."
            )
            raise NotAllowedError(msg)

        if self._is_active():
            if self.mode == "free":
                existing_games = get_multiple_games_by_id(self.elements["g"])
                for g in existing_games:
                    if not g.finished:
                        msg = (
                            "Attempted to add a new game, "
                            f"although game with id {g.id} "
                            "has not yet been finished."
                        )
                        raise(NotAllowedError(msg))

                for pid in game.get_player_ids():
                    if pid not in self.elements["p"]:
                        msg = f"Player with id {pid} not in this event."
                        raise(NotAllowedError(msg))

                self.elements["g"].append(game.id)
            else:
                raise(NotImplementedError)
            
            self.save()
            logger.debug(f"Game[{game.id}] was added to Event[{self}].")

    def _is_active(self):
        if self.active:
            return True
        else:
            raise(NotAllowedError("Event is not active."))

    def activate(self):
        if not self.active:
            active_ev_ids = [
                ev.id for ev in Event.select().where(Event.active == True)]
            active_ev_ids = [evid for evid in active_ev_ids if evid != self.id]
            if active_ev_ids:
                msg = (
                    "Can not activate event, "
                    "because there exists an active event "
                    f"with ID {active_ev_ids[0]}."
                )
                raise(NotAllowedError(msg))
            self.active = True
            self.save()
            logger.debug(f"Event[{self}] activated.")

    def deactivate(self):
        game = self.get_active_game()
        if game:
            msg = (
                "Event can not be deactivated, because "
                f"there is an active game with ID {game}"
            )
            raise(NotAllowedError(msg))
        else:
            if self.active:
                self.active = False
                self.save()
                logger.debug(f"Event[{self}] deactivated.")

    def get_active_game(self):
        games = get_multiple_games_by_id(self.elements["g"])
        active_games = [g for g in games if g.finished == False]
        if len(active_games) == 1:
            return active_games[0]
        elif len(active_games) > 1:
            raise(FatalError("Found more than one active game."))


#################################################################
#################################################################


class Player(BaseModel):
    name = CharField(unique=True)
    created = DateTimeField(default=datetime.now)

    def played_games(self, position=("d", "o"), side=("w", "b"), mode=("m", "s")):
        query = Game.select().where(
            (Game.pbd == self) |
            (Game.pbo == self) |
            (Game.pwd == self) |
            (Game.pwo == self)
        )
        all_games = [p for p in query.order_by(Game.id)]

        return_games = []
        for g in all_games:
            expression = (
                (g.get_position_by_player(self) in position) &
                (g.get_side_by_player(self) in side) &
                (g.get_mode_by_player(self) in mode)
            )
            if expression:
                return_games.append(g)

        return return_games


#################################################################
#################################################################


class Game(BaseModel): # TODO process event
    # General information
    created = DateTimeField(default=datetime.now)
    started = BooleanField(default=False)
    finished = BooleanField(default=False)
    event = ForeignKeyField(Event)
    # Player information
    single_b = BooleanField()
    single_w = BooleanField()
    pbd = ForeignKeyField(Player)
    pbo = ForeignKeyField(Player)
    pwd = ForeignKeyField(Player)
    pwo = ForeignKeyField(Player)
    # Game information
    playto = IntegerField(default=6)
    history = CharField(default="")

    def add_player(self, black, white):
        assert type(black) == list
        assert type(white) == list
        assert any(p in white for p in black) == False

        # Add black players
        if len(black) == 1:
            self.pbd = black[0]
            self.pbo = black[0]
            self.single_b = True
        elif len(black) == 2:
            self.pbd = black[0]
            self.pbo = black[1]
            self.single_b = False
        else:
            msg = "Length of black must equals 1 or 2"
            raise(ValueError(msg))

        # Add white players
        if len(white) == 1:
            self.pwd = white[0]
            self.pwo = white[0]
            self.single_w = True
        elif len(white) == 2:
            self.pwd = white[0]
            self.pwo = white[1]
            self.single_w = False
        else:
            msg = "Length of white must equals 1 or 2"
            raise(ValueError(msg))

        self.save()
        player = [self.pbd, self.pbo, self.pwd, self.pwo]
        logger.debug(f"Added Player {player} to Game[{self}].")
        logger.debug(f"Game[{self}] saved.")

    def goal(self, side, slot):
        if self.finished:
            raise(NotAllowedError("Game is already finished."))
        if side == "b" and slot == "d":
            msg = "gbd"
        elif side == "b" and slot == "o":
            msg = "gbo"
        elif side == "w" and slot == "d":
            msg = "gwd"
        elif side == "w" and slot == "o":
            msg = "gwo"
        self._add_to_history(msg)

    def owner(self, side, slot):
        if self.finished:
            raise(NotAllowedError("Game is already finished."))
        if side == "b" and slot == "d":
            msg = "obd"
        elif side == "b" and slot == "o":
            msg = "obo"
        elif side == "w" and slot == "d":
            msg = "owd"
        elif side == "w" and slot == "o":
            msg = "owo"
        self._add_to_history(msg)

    def goal_and_owner_by_key(self, key):
        if self.finished:
            raise(NotAllowedError("Game is already finished."))
        assert key in ["gbd", "gbo", "gwd", "gwo", "obd", "obo", "owd", "owo"]
        self._add_to_history(key)

    def _decode(self):
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

    def _add_to_history(self, msg):
        sep = "_" if self.history else ""
        self.history += sep + msg
        self._update_pre()
        logger.debug(f"Added '{msg}' to history for Game[{self}].")
        self._update_post_and_save()
        

    def undo(self):
        msgs = self.history.split("_")
        msgs = msgs[:-1]
        self.history = "_".join(msgs)
        self._update_pre()
        if self.finished:
            logger.debug(f"Reopen Game[{self}]")
        logger.debug(f"Undid last action for Game[{self}].")
        self._update_post_and_save()
        

    def get_score(self):
        counters = self._decode()
        gb = counters["gbd"] + counters["gbo"]
        gw = counters["gwd"] + counters["gwo"]
        ob = counters["obd"] + counters["obo"]
        ow = counters["owd"] + counters["owo"]

        return {"b": gb + ow, "w": gw + ob}

    def _update_pre(self):
        if self.history and not self.started:
            logger.debug(f"Started Game[{self}].")
        self.started = bool(self.history)
            
    def _update_post_and_save(self):
        score = self.get_score()
        finished = score["b"] >= self.playto or score["w"] >= self.playto
    
        if not self.finished and finished:
            logger.debug(f"Finished Game[{self}].")
            
        self.finished = finished
        self.save()

    def switch_sides(self):
        if self.started:
            raise(NotAllowedError("Unable to switch sides, game has already started."))

        pbd = self.pbd
        pbo = self.pbo
        pwd = self.pwd
        pwo = self.pwo
        sb = self.single_b
        sw = self.single_w

        self.pbd = pwd
        self.pbo = pwo
        self.pwd = pbd
        self.pwo = pbo
        self.single_b = sw
        self.single_w = sb

        self.save()
        logger.debug(f"Switched sides of Game[{self}].")

    def switch_slots(self, side):
        if self.started:
            raise(NotAllowedError("Unable to switch slots, game has already started."))

        pbd = self.pbd
        pbo = self.pbo
        pwd = self.pwd
        pwo = self.pwo

        if side == "b":
            self.pbd = pbo
            self.pbo = pbd
            log_str = "black"
        elif side == "w":
            self.pwd = pwo
            self.pwo = pwd
            log_str = "white"

        self.save()
        logger.debug(f"Switched {log_str} side of Game[{self}].")

    def get_player_ids(self, side=None):
        b = set((self.pbd.id, self.pbo.id))
        w = set((self.pwd.id, self.pwo.id))

        if side == "b":
            return tuple(b)
        elif side == "w":
            return tuple(w)
        else:
            return tuple(b | w)

    def get_position_by_player(self, player):
        if player in [self.pbd, self.pwd]:
            return "d"
        elif player in [self.pbo, self.pwo]:
            return "o"

    def get_side_by_player(self, player):
        if player in [self.pbd, self.pbo]:
            return "b"
        elif player in [self.pwd, self.pwo]:
            return "w"

    def get_mode_by_player(self, player):
        if player in [self.pbd, self.pbo]:
            return "s" if self.single_b else "m"
        elif player in [self.pwd, self.pwo]:
            return "s" if self.single_w else "m"


db.create_tables([Player, Game, Event])


#################################################################
#################################################################


def new_player(name):
    try:
        p = Player(name=name)
        p.save()
        logger.debug(f"Player[{p.id}] '{name}' created and saved.")
    except:
        raise NotAllowedError(f"Player[{p.id}] '{name}' already exists.")
    return p


def new_game(event):
    g = Game(event=event)
    logger.debug(f"Empty game created.")
    return g


###############################


def get_game_by_id(game_id):
    try:
        return Game[game_id]
    except:
        raise(NotFoundError(f"No game with id {game_id} found."))


def get_multiple_games_by_id(game_ids):
    try:
        return [g for g in Game.select().where(Game.id << game_ids)]
    except:
        raise(NotFoundError(f"No games with given ID's found."))


###############################


def get_player_by_id(player_id):
    try:
        return Player[player_id]
    except:
        raise(NotFoundError(f"No player with id {player_id} found."))


def get_multiple_player_by_id(player_ids):
    try:
        return [p for p in Player.select().where(Player.id << player_ids)]
    except:
        raise(NotFoundError(f"No player with given ID's found."))


def get_player_by_name(player_name):
    try:
        return Player.select().where(Player.name == player_name).get()
    except:
        raise(NotFoundError(f"No player with name {player_name} found."))


def get_multiple_player_by_name(player_names):
    try:
        return [p for p in Player.select().where(Player.name << player_names)]
    except:
        raise(NotFoundError(f"No players with given names found."))


###############################


def get_event_by_id(event_id):
    try:
        return Event[event_id]
    except:
        raise(NotFoundError(f"No event with id {event_id} found."))


def get_multiple_events_by_id(event_ids):
    try:
        return [ev for ev in Event.select().where(Event.id << event_ids)]
    except:
        raise(NotFoundError(f"No events with given ID's found."))
