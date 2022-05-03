from abc import ABC


class GameLogic(ABC):
    """Abstract Base Class that defines an interface for logic elements such as Rooms and Combat."""
    def __init__(self, name):
        self.name = name

    def submit(self, user_input: int) -> [str, None]:
        """Take in a user input, return a new string to display"""

    @property
    def options(self) -> list[str]:
        return []
