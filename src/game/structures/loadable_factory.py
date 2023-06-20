from loguru import logger

from game.cache import get_cache, get_loader
from game.structures.loadable import LoadableMixin
from game.systems.requirement import requirements


class LoadableFactory:

    @classmethod
    def collect_requirements(cls, json: dict, field='requirements') -> list[requirements.Requirement]:
        """
        Interrogate a JSON blob and parse out any requirements it has stored inside.

        Notably, this method expects the JSON blob to store its requirements at a top-level under the
        field 'requirements'.
        """

        if field not in json:
            return None

        reqs = []

        for requirement_json in json[field]:
            req = LoadableFactory.get(requirement_json)
            if not isinstance(req, requirements.Requirement):
                raise TypeError(f"Expected requirement of type Requirement, got {type(req)} instead!")

            reqs.append(req)

        return reqs

    @classmethod
    def collect_resource_modifiers(cls, json: dict, field='resource_modifiers') -> dict[str, int | float]:
        """
        Interrogate a JSON blob and parse out any resource_modifiers it has stored inside.

        Notably, this method expects the JSON blob to store its resource modifiers at a top-level under the
        field 'resource_requirements'.
        """

        return json[field] if field in json else None

    @classmethod
    def collect_optional_fields(cls, fields: list[tuple[str, type]], json: dict,
                                implicit_fields: bool = True) -> dict:
        """
        Search for optional fields within a JSON blob and bundle them into a dict. Any fields not found will simply not
        be included.
        """
        kw = {}

        for field_name, field_type in fields:

            if field_name in json:  # If the JSON blob contains a matching field
                if field_type == dict:  # If it is a dict and can possibly be a dict-form of a supported class
                    if 'class' in json[field_name]:  # Search for class field
                        kw[field_name] = LoadableFactory.get(json[field_name])  # Instantiate the object from dict
                        continue

                kw[field_name] = json[field_name]  # Fall back and store the original dict

        if implicit_fields:
            res_mod = cls.collect_resource_modifiers(json)
            req = cls.collect_requirements(json)

            logger.debug(str(res_mod))
            logger.debug(str(req))

            if res_mod is not None:
                kw['resource_modifiers'] = res_mod

            if req is not None:
                kw['requirements'] = req

        logger.debug(kw)

        return kw

    @classmethod
    def validate_fields(cls, fields: list[tuple[str, type]], json: dict, required=True, implicit_fields=True) -> bool:
        """
        Verify that the expected json fields are present and correctly typed.

        args:
            fields: A list of tuples mapping each field to a type
            json: A dict-form representation of a json object
            required: If True, treat each field as if it is required and throw an error if it is missing
            implicit_fields: If True, add in a set of pre-defined common fields in the background.

        returns: True if all the fields are present and correctly typed.
        """
        base_fields = [('class', str)]

        for field_name, field_type in fields + (base_fields if implicit_fields else []):

            # Verify valid tuple typings
            if type(field_name) != str:
                raise TypeError(f"field_name must be of type 'str'! Got {type(field_name)} instead.")

            if type(field_type) != type:
                raise TypeError(f"field_type must be of type 'type' Got {type(field_type)} instead.")

            # Verify field presence
            if field_name not in json and required:
                raise ValueError(f"Field {field_name} not found!")

            # Verify field types
            elif field_name in json and type(json[field_name]) != field_type:
                raise TypeError(
                    f"Field {field_name} wrong type! Expected type {field_type}, "
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

        if json["class"] not in get_cache()[LoadableMixin.LOADER_KEY]:
            raise ValueError(f"No loader for class {json['class']} has been registered!")

        try:
            return get_loader(json['class'])(json=json)

        except Exception as e:
            logger.error(f"Something wen wrong while trying to load an object of type {json['class']}!")
            raise e
