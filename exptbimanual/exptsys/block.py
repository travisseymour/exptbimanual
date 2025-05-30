
class Block:
    def __init__(self):
        self.items: list = []

    def run(self):
        for item in self.items:
            item.run()