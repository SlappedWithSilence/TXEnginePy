"""
A utility python file that hosts a global cache, global config, and useful accessor/setter methods
"""
from typing import Callable

config: dict[str, any] = None
cache: dict[str, any] = {}


def get_cache() -> dict:
    """
    Retrieve a reference to the cache
    """
    global cache
    return cache


def set_config(cfg: dict) -> None:
    """
    Set the config dict
    """
    global config
    config = cfg


def get_config() -> dict:
    """
    Retrieve a reference to the config dict
    """
    global config
    return config


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
