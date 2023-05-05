from game.cache import cached, get_cache, get_loader


class LoadableMixin:
    """An interface for classes that need to define logic for building an instance from JSON"""

    CLASS_KEY = "LoadableMixin"
    LOADER_KEY: str = 'loader'
    ATTR_KEY: str = "from_json"
    CACHE_PATH: list[str] = [LOADER_KEY, CLASS_KEY, ATTR_KEY]

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    @cached(CACHE_PATH)
    def from_json(json: dict[str, any]) -> any:
        raise NotImplementedError()


class LoadableFactory:

    @classmethod
    def validate_required_fields(cls, required_fields: list[tuple[str, type]], json: dict) -> bool:
        """
        Verify that the expected json fields are present and correctly typed
        """
        for field_name, field_type in required_fields:

            # Verify field presence
            if field_name not in json:
                raise ValueError(f"Required field {field_type} not found!")

            # Verify field types
            if type(json[field_name]) != field_type:
                raise TypeError(
                    f"Required field {field_type} wrong type! Expected type {field_type.__name__}, "
                    f"got type {type(json[field_name])} instead!"
                )

        return True

    @classmethod
    def get(cls, json: dict[str, any]) -> any:
        """
        Instantiate a Loadable object from a JSON blob.

        Args:
            json: a dict-form representation of a Loadable object

        Returns: An object of the type specified in the JSON.
        """

        if type(json) != dict:
            raise TypeError(f"Argument 'json' must be of type dict, got type {type(json)} instead!")

        if "class" not in json:
            raise ValueError("Cannot load a JSON blob without a class field!")

        if json["class"] not in get_cache()['loader']:
            raise ValueError(f"No loader for class {json['class']} has been registered!")

        return get_loader(json['class'])(json=json)
