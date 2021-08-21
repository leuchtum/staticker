from .core import Event


class Manager:
    def __init__(self):
        self.active_event = None
        self.active_game = None
        
        self._update_active_event()

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


manager = Manager()
