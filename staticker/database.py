from tinydb import Query, TinyDB
import pathlib
import platform
import random
from datetime import datetime

FOLDER_NAME = ".staticker"
DATABASE_NAME = "database.json"
LOOKUP = {"team":"T", "player":"P", "game":"G", "session":"S"}

###############################################################
###############################################################

class Database():

#–––––––––––––––––––––––––––––––––––––––––––––––– INIT

    def __init__(self):

        self.os = platform.system()

        self.folder_path = pathlib.Path.home()
        self.folder_path = pathlib.Path(self.folder_path,FOLDER_NAME)

        if not self.folder_path.exists():
            self.folder_path.mkdir()

        self.db_path = pathlib.Path(self.folder_path,DATABASE_NAME)
        self.root_db = TinyDB(str(self.db_path))

        for name in LOOKUP:
            setattr(self,name,self.root_db.table(name))

#–––––––––––––––––––––––––––––––––––––––––––––––– GETTER

    def get_existing_ids(self):
        tables = self.root_db.tables()
        tables = [getattr(self, t) for t in tables]
        existing = []
        for table in tables:
            keys = table.all()
            keys = [k["id"] for k in keys]
            existing.extend(keys)
        return existing

#–––––––––––––––––––––––––––––––––––––––––––––––– OTHER

    def delete(self):
        self.tables = {}
        self.db_path.unlink()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __del__(self):
        self.root_db.close()

#################################################
#################################################

class Handler:

#–––––––––––––––––––––––––––––––––––––––––––––––– INIT

    def __init__(self):
        self._db = Database()

#–––––––––––––––––––––––––––––––––––––––––––––––– OTHER

    def dump(self, obj):
        tablename = obj._tablename
        dic = obj.dict(
            exclude_none=True,
            exclude_defaults=True
        )
        table = getattr(self._db, tablename)
        table.upsert(dic, Query().id == obj.id)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def load_one(self, tablename, obj_id):
        table = getattr(self._db, tablename)
        return table.get(Query().id == obj_id)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def load_multiple(self, tablename, obj_ids: list):
        table = getattr(self._db, tablename)
        return table.search(Query().id.one_of(obj_ids))

#––––––––––––––––––––––––––––––––––––––––––––––––

    def load_all(self, tablename):
        table = getattr(self._db, tablename)
        return table.all()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def new_key(self):
        existing = self._db.get_existing_ids()
        while True:
            digits = "".join([
                "0123456789",
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "abcdefghijklmnopqrstuvwxyz"])
            digits = random.choices(digits, k=8)
            key = "".join(digits)
            if key not in existing:
                break
        return key

#––––––––––––––––––––––––––––––––––––––––––––––––

    def random_name(self):
        name = [
            "Loine",
            "Andi",
            "Becky",
            "Bernd",
            "Michael",
            "Anna",
            "Marie"
        ]
        surname = [
            "Lechner",
            "Müller",
            "Maier",
            "Schmidt",
            "Abend",
            "Morgen",
            "Vogel"
        ]
        name = random.choice(name)
        surname = random.choice(surname)
        num = str(random.choice(range(10)))
        return "_".join([name, surname, num])

#––––––––––––––––––––––––––––––––––––––––––––––––

    def now(self):
        return datetime.now().timestamp()

#################################################
#################################################

class SingleBase:

#––––––––––––––––––––––––––––––––––––––––––––––––

    def dump(self):
        h = Handler()
        h.dump(self)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def load(self, obj_id):
        h = Handler()
        dic = h.load_one(self._tablename, obj_id)
        if not dic:
            msg = f"No object in table {self._tablename.upper()} with ID={obj_id} found."
            raise TypeError(msg)
        self.__init__(**dic)

#################################################
#################################################

class MultiBase:

    def __init__(self):
        self.objects = []
#––––––––––––––––––––––––––––––––––––––––––––––––

    def load(self, obj_ids: list):
        self.objects = []
        h = Handler()
        obj_list = h.load_multiple(self._tablename, obj_ids)
        for dic in obj_list:
            self.objects.append(self._class(**dic))

#––––––––––––––––––––––––––––––––––––––––––––––––

    def add(self, obj_id: str):
        h = Handler()
        dic = h.load_one(self._tablename, obj_id)
        self.objects.append(self._class(**dic))

#––––––––––––––––––––––––––––––––––––––––––––––––

    def load_all(self):
        self.objects = []
        h = Handler()
        obj_all = h.load_all(self._tablename)
        for dic in obj_all:
            self.objects.append(self._class(**dic))

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_objects(self):
        return self.objects

#––––––––––––––––––––––––––––––––––––––––––––––––

    def load_and_sort(self, dic: dict):
        loads = list(dic.keys())
        self.load(loads)
        self.sort(dic)

#––––––––––––––––––––––––––––––––––––––––––––––––

    def sort(self, *kwargs):
        obj_list = []
        has_name = False

        for obj in self.objects:
            dic = {"obj": obj}
            for i in range(len(kwargs)): 
                dic[i] = kwargs[i][obj.id]
            if hasattr(obj, "name"):
                has_name = True
                dic["name"] = obj.name
            obj_list.append(dic)

        if has_name:
            if len(kwargs) == 0:
                keys = lambda d: (d["name"])
            else:
                if i == 0:
                    keys = lambda d: (-d[0], d["name"])
                elif i == 1:
                    keys = lambda d: (-d[0], -d[1], d["name"])
        else:
            if len(kwargs) == 0:
                return None
            if i == 0:
                keys = lambda d: (-d[0])
            elif i == 1:
                keys = lambda d: (-d[0], -d[1])

        self.objects = [d["obj"] for d in sorted(obj_list, key=keys)]

#################################################
#################################################

