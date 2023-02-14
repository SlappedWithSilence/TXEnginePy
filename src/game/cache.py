"""
A utility python file that hosts a global cache, global config, and useful accessor/setter methods
"""

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
