from loguru import logger

from game.cache import get_cache


# TODO: Improve Loadable to set loader on import, not on instantiation

class LoadableMixin:
    """An interface for classes that need to define logic for building an instance from JSON"""

    LOADER_KEY: str = 'loader'
    already_assigned: bool = False

    def __init__(self):
        if not self.already_assigned:
            cache = get_cache()

            # Build loader cache if it doesn't exist
            if self.LOADER_KEY not in cache:
                logger.info("Creating loader cache...")
                cache[self.LOADER_KEY] = {}

            # If the loader has not already been assigned and doesn't already exist
            if self.__class__.__name__ not in cache[self.LOADER_KEY]:
                logger.info(f"Assigning loader function to class {self.__class__.__name__}")
                cache[self.LOADER_KEY][self.__class__.__name__] = self.from_json
                self.already_assigned = True

            # If the loader is
            elif cache[self.LOADER_KEY][self.__class__.__name__] == self.from_json:
                pass
            else:
                raise RuntimeError(f"Cannot assign JSON loader function to class {self.__class__.__name__}! A different "
                                   f"loader function already exists.")

    @classmethod
    def from_json(cls, json: dict[str, any]) -> any:
        raise NotImplementedError()
