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


def get_loader(cls: type | str) -> Callable:
    """
    A convenience wrapper that fetches loader functions from the cache for a given class.

    args:
        cls: Either a type or a string representation of a type whose loader to fetch

    returns: A reference to the requested loader function
    """

    key = str(cls)
    if key in get_cache()['loader']:
        return get_cache()['loader'][key]

    else:
        raise KeyError(
            f"No loader found for class {key}! Available loaders:\n{' '.join(list(get_cache()['loader'].keys()))}"
        )


def cached(root_key: str, attr_key: str) -> Callable:
    """
    A parameterized decorator that caches a given function under the key 'root_key' and sub-key 'attr_key'.

    For example,
    @cached('fancy', 'func')
    def some_func():
        pass

    would cache some_func under:
    get_cache()['fancy']['func']

    args:
        root_key: The root-level key under which to cache the func
        attr_key: The second-level key under which to cache the func

    returns: The base-level decorator
    """
    def decorate(func: Callable):

        if root_key not in get_cache():
            get_cache()[root_key] = {}

        if attr_key not in get_cache()[root_key]:
            get_cache()[root_key][attr_key] = func

        elif get_cache()[root_key][attr_key] != func:
            raise RuntimeError(f"Cannot cache [{root_key}][{attr_key}]! Something else was already cached!")

        return func

    return decorate
