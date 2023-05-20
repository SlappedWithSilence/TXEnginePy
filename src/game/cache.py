"""
A utility python file that hosts a global cache, global config, and useful accessor/setter methods
"""
from typing import Callable

config: dict[str, any] = None
cache: dict[str, any] = {}


def decode_path(path: list[str] | str) -> list[str]:
    """
    Decodes a path and returns a list[str] via dot-notation.
    """

    if type(path) != list and type(path) != str:
        raise TypeError(f"Unexpected cache path type: {type(path)}! Allowed types are list[str] and str!")
    elif type(path) == list:
        for key in path:
            if type(key) != str:
                raise TypeError(f"Unexpected type within a listed cache path: {type(key)}! Allowed types are str")
        return path
    elif type(path) == str:
        return path.split('.')


def from_cache(path: list[str] | str) -> any:
    """
    A universal cache-retrieval function.

    Elements cached can be retrieved via their dict-path using a list of keys or string dot-notation.

    args:
        path: A list of nested dict keys or a string of dot notation

    returns:
        The element in the cache stored at the lowest level of the dict-path
    """

    true_path = decode_path(path)

    depth = get_cache()
    for key in true_path[:-1]:  # Skip last key in path
        if key not in depth:
            raise KeyError()
        if type(depth[key]) != dict:
            raise TypeError(f"Expected key {key}'s value to be of type dict! Got {type(depth[key])} instead.")

        depth = depth[key]

    return depth[true_path[-1]]


def cache_element(path: list[str] | str, element: any) -> None:
    """
    Universal logic for caching an element in the cache. Using a collection of strings or a dot-notated path string,
    cache an object along a dict-path of 'path'.
    """

    true_path = decode_path(path)

    depth = get_cache()
    for key in true_path[:-1]:
        if key in depth and type(depth[key]) != dict:
            raise KeyError("Cannot create path dict in cache! A collision was detected.")

        elif key in depth and type(depth[key] == dict):
            pass

        else:
            depth[key] = {}

        depth = depth[key]

    depth[path[-1]] = element


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
    from game.structures.loadable import LoadableMixin

    key = str(cls)
    loader_base_path = [LoadableMixin.LOADER_KEY]
    loader_full_path = loader_base_path + [key, LoadableMixin.ATTR_KEY]

    if key in from_cache(loader_base_path):
        return from_cache(loader_full_path)

    else:
        raise KeyError(
            f"No loader found for class {key}! Available loaders:\n{' '.join(list(get_cache()['loader'].keys()))}"
        )


def cached(path: list[str] | str) -> Callable:
    """
    A parameterized decorator that caches a given function under the key 'root_key' and sub-key 'attr_key'.

    For example:

    @cached(['fancy', 'func'])
    def some_func():
        pass

    or alternatively:

    @cached("fancy.func")
    def some_func():
        pass

    would cache some_func under:
    get_cache()['fancy']['func']

    args:
       path: A list of strings or a string following dot-notation that describes the dict-path where the element should
       be stored.

    returns: The base-level decorator
    """

    def decorate(func: Callable):
        cache_element(path, func)

        return func

    return decorate
