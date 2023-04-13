from loguru import logger

from game.cache import get_cache


class LoadableMixin:
    """An interface for classes that need to define logic for building an instance from JSON"""

    LOADER_KEY = 'loader'

    def __init__(self):
        cache = get_cache()
        if self.LOADER_KEY not in cache:
            logger.info("Creating loader cache...")
            cache[self.LOADER_KEY] = {}

        if self.__class__.__name__ not in cache[self.LOADER_KEY]:
            logger.info(f"Assigning loader function to class {self.__class__.__name__}")
            cache[self.LOADER_KEY][self.__class__.__name__] = self.from_json

        elif cache[self.LOADER_KEY] == self.from_json:
            pass
        else:
            raise RuntimeError(f"Cannot assign JSON loader function to class {self.__class__.__name__}! A different "
                               f"loader function already exists.")

    @classmethod
    def from_json(cls, json: dict[str, any]) -> any:
        raise NotImplementedError()
