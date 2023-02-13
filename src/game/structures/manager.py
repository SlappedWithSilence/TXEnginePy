from abc import ABC

from loguru import logger


class Manager(ABC):
    """
    An interface for defining manager behavior. A manager must:
    - Define loading behavior
    - Define saving behavior
    """

    def __init__(self):
        self.name = self.__class__.__name__
        logger.info("Registering with cache...")

    def load(self) -> None:
        raise NotImplementedError

    def save(self) -> None:
        raise NotImplementedError
