from abc import ABC


class Manager(ABC):

    def __init__(self):
        self.name = self.__class__.__name__

    def load(self) -> None:
        raise NotImplementedError

    def save(self) -> None:
        raise NotImplementedError
