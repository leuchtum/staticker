import pathlib
import platform
import shutil

FOLDER_NAME = ".staticker"
DATABASE_NAME = "database.db"


class DBDirectory():

    def __init__(self):

        self.os = platform.system()

        self.home = pathlib.Path.home()
        self.folder_path = pathlib.Path(self.home, FOLDER_NAME)
        self.db_path = pathlib.Path(self.folder_path, DATABASE_NAME)

    def mk_dir(self):
        if not self.folder_path.exists():
            self.folder_path.mkdir()

    def get_db_path(self):
        return self.db_path

    def del_db(self):
        if self.db_path.exists():
            self.db_path.unlink()
            
    def del_folder(self):
        if self.folder_path.exists():
            shutil.rmtree(str(self.folder_path))