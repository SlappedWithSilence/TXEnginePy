from game.cache import cached


class LoadableMixin:
    """An interface for classes that need to define logic for building an instance from JSON"""

    LOADER_KEY: str = 'loader'
    ATTR_KEY: str = "from_json"
    CACHE_PATH: str = LOADER_KEY + ".{}." + ATTR_KEY

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    @cached(CACHE_PATH.format("LoadableMixin"))
    def from_json(json: dict[str, any]) -> any:
        raise NotImplementedError()


