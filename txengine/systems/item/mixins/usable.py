class UsableMixin:
    def __init__(self):
        self.effects: list = []  # A list of effects to be executed when the item is used
        self.on_use: str = None  # A string to be printed when the item is used

    