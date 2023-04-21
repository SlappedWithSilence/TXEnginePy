import game.cache as cache

from abc import ABC
import weakref

from loguru import logger


class Manager(ABC):
    """
    An interface for defining manager behavior. A manager must:
    - Define loading behavior
    - Define saving behavior
    """

    def __init__(self):
        self.name = self.__class__.__name__

        if "managers" not in cache.get_cache():
            logger.debug("Creating managers cache...")
            cache.get_cache()["managers"] = {}

        logger.debug(f"[{self.name}] Registering manager with cache...")
        cache.get_cache()["managers"][self.name] = weakref.proxy(self)

    def load(self) -> None:
        raise NotImplementedError

    def save(self) -> None:
        raise NotImplementedError
