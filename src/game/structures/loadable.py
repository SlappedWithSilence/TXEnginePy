from game.cache import cached


class LoadableMixin:
    """An interface for classes that need to define logic for building an instance from JSON"""

    LOADER_KEY: str = 'loader'
    ATTR_KEY: str = "from_json"

    @cached(LOADER_KEY, "LoadableMixin")
    def from_json(self, json: dict[str, any]) -> any:
        raise NotImplementedError()
