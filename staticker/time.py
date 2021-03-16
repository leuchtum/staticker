from datetime import datetime
from pydantic import BaseModel

class Time(BaseModel):
    begin: float = None
    end: float = None

#––––––––––––––––––––––––––––––––––––––––––––––––

    def __init__(self, **data):
        super().__init__(**data)
        if not self.begin:
            self.begin = datetime.now().timestamp()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def stop(self):
        self.end = datetime.now().timestamp()

#––––––––––––––––––––––––––––––––––––––––––––––––

    def get_duration(self):
        if self.end:
            end = datetime.fromtimestamp(self.end)
            begin = datetime.fromtimestamp(self.begin)
            return float((end - begin).total_seconds())
        else:
            return False