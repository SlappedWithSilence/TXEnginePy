import weakref

config: dict[str, any] = None
cache: dict[str, any] = {}


def get_cache() -> dict:
    global cache
    return cache


def set_config(cfg: dict) -> None:
    global config

    config = cfg


def get_config() -> dict:
    global config
    return config
