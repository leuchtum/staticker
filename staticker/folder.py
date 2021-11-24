import pathlib
import platform
import shutil
from .log import logger

FOLDER_NAME = ".staticker"
DATABASE_NAME = "staticker.db"


class DBDirectory:
    def __init__(self):

        self.os = platform.system()

        self.home = pathlib.Path.home()
        self.folder_path = pathlib.Path(self.home, FOLDER_NAME)
        self.db_path = pathlib.Path(self.folder_path, DATABASE_NAME)

    def mk_dir(self):
        if not self.folder_path.exists():
            self.folder_path.mkdir()
            logger.debug(f"Created folder {self.folder_path}")

    def get_db_path(self):
        return self.db_path

    def del_db(self):
        if self.db_path.exists():
            self.db_path.unlink()
            logger.debug(f"Deleted database {self.db_path}")

    def del_folder(self):
        if self.folder_path.exists():
            shutil.rmtree(str(self.folder_path))
            logger.debug(f"Deleted folder {self.folder_path}")
