from .core import Event
from .communication import arduino


class Manager:
    def __init__(self):
        self._update_active_event()
        arduino.set_callback(self._process_serial_event)

    def _update_active_event(self):
        query = Event.select().where(Event.active == True)
        try:
            self.active_event = query.get()
        except:
            self.active_event = None

    def get_active_event(self):
        self._update_active_event()
        return self.active_event

    def get_active_game(self):
        ev = self.get_active_event()
        if ev:
            return ev.get_active_game()

    async def startup(self):
        await arduino.start_listen()

    def is_arduino_available(self):
        return arduino.available

    def _process_serial_event(self, dic):
        print(dic)
        mode = dic["mode"]
        
        if mode == "pressed":
            active_game = self.get_active_game()
            if active_game:
                active_game.goal_and_owner_by_key(dic["msg"])
            else:
                pass
        elif mode == "error":
            msg = dic["msg"]
            raise Exception(f"Error from Arduino: {msg}")


manager = Manager()
