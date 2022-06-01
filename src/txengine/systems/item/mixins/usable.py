from src.txengine.systems.effect import Effect


class UsableMixin:
    def __init__(self):
        self.effects: list[Effect] = []  # A list of effects to be executed when the item is used
        self.on_use: str = None  # A string to be printed when the item is used
        self.consumable = False

    def use(self):
        for effect in self.effects:
            effect.perform()
