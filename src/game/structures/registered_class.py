from game.cache import get_cache

from loguru import logger


def registered_class(root_key_attr: str, cached_attr: str):
    """
    A Class decorator that caches a specified attribute globally.

    For example, if:
    - cls == SomeClass
    - root_key_attr == "ROOT_KEY"
    - cached_attr == "some_func"

    @registered_class("ROOT_KEY", "some_func")
    class SomeClass:
        ROOT_KEY = "a key"

        def some_func():
            pass

    This function would attempt to cache SomeClass::some_func in get_cache()[SomeClass::ROOT_KEY].
    That is to say, it would run get_cache()[SomeClass::ROOT_KEY] = SomeClass::some_func.

    This is useful when a class needs to store one of its class functions or static functions globally BEFORE any
    object of that type is instanced.
    """

    def decorate(cls) -> type:

        if root_key_attr not in cls.__dict__:
            raise ValueError(f"Cannot locate root key attribute {root_key_attr} for class {cls.__name__}!")

        if cached_attr not in cls.__dict__:
            raise ValueError(f"Cannot locate attribute to cache ({cached_attr}) in class {cls.__name__}")

        if cls.__getattribute__(root_key_attr) not in get_cache():
            get_cache()[cls.__getattribute__(root_key_attr)] = {}

        if cls.__name__ not in get_cache()[cls.__getattribute__(root_key_attr)]:
            get_cache()[cls.__getattribute__(root_key_attr)][cls.__name__] = cls.__getattribute__(cached_attr)
            logger.info(f"Registered {cached_attr} of class {cls.__name__} in cache.")

        elif get_cache()[cls.__getattribute__(root_key_attr)][cls.__name__] != cls.__getattribute__(cached_attr):
            raise RuntimeError(f"Cannot cache {cached_attr} for class {cls.__name__}, something else was already cached!")

        return cls
    return decorate
