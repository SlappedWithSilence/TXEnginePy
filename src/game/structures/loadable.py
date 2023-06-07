from game.cache import cached


class LoadableMixin:
    """An interface for classes that need to define logic for building an instance from JSON"""

    LOADER_KEY: str = 'loader'
    ATTR_KEY: str = "from_json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    @cached(["loader", "LoadableMixin", "from_json"])
    def from_json(json: dict[str, any]) -> any:
        raise NotImplementedError()
