from typing import Callable

from game.cache import get_cache


# TODO: Improve Loadable to set loader on definition


def cached(root_key: str, attr_key: str) -> Callable:

    def decorate(func: Callable):

        if root_key not in get_cache():
            get_cache()[root_key] = {}

        if attr_key not in get_cache()[root_key]:
            get_cache()[root_key][attr_key] = func

        elif get_cache()[root_key][attr_key] != func:
            raise RuntimeError(f"Cannot cache [{root_key}][{attr_key}]! Something else was already cached!")

        return func

    return decorate


class LoadableMixin:
    """An interface for classes that need to define logic for building an instance from JSON"""

    LOADER_KEY: str = 'loader'
    ATTR_KEY: str = "from_json"

    def __init__(self):
        if self.ATTR_KEY not in self.__dict__:
            raise RuntimeError(f"{self.__class__.__name__} is Loadable but does not implement {self.ATTR_KEY}!")

    @cached(LOADER_KEY, "LoadableMixin")
    def from_json(self, json: dict[str, any]) -> any:
        raise NotImplementedError()
