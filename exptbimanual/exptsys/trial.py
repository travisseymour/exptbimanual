from exptbimanual.exptsys.trialevent import TrialEvent


class Trial:
    def __init__(self):
        self.events: list[TrialEvent] = []

    def run(self):
        for event in self.events:
            event.run()