from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Union

from loguru import logger

import game.structures.loadable_factory
from game.cache import from_cache, cached
from game.structures.loadable import LoadableMixin
from game.structures.messages import StringContent


class Requirement(LoadableMixin, ABC):
    """
    An abstract object that defines broad logical parameters that must be met. Children of this class narrow that logic
    and allow other objects to compose them to enforce a wide variety of gameplay mechanics.
    """

    def fulfilled(self, entity) -> bool:
        """
        Computes whether the requirement is fulfilled by the owner
        Returns: True if the requirement is fulfilled, False otherwise

        """
        raise NotImplementedError()

    @property
    def description(self) -> list[str | StringContent]:
        """
        Args:
        Returns:
            A list of strings and StringContents that provides the reader with a textual representation of the
            conditions that are specified for this Requirement to be 'fulfilled' such that self. Fulfilled==True
        """
        raise NotImplementedError()

    def __str__(self):
        """Return a conjoined string that strings self. Description of styling data"""
        return " ".join([str(e) for e in self.description])


class RequirementsMixin:
    """
    A mixin class that enables a child class to accept requirements.
    """

    def __init__(self, requirements: list[Requirement] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requirements: list[Requirement] = requirements or None

    def is_requirements_fulfilled(self, entity) -> bool:
        """
        Calculates if all the requirements are fulfilled
        Returns: True if all requirements are fulfilled, False otherwise

        """

        return all([req.fulfilled(entity) for req in self.requirements])

    def get_requirements_as_str(self) -> list[str]:
        """Get a list of strings that represent the conditions for the requirements associated with this object"""
        return [str(r) for r in self.requirements]

    def get_requirements_as_options(self) -> list[list[str | StringContent]]:
        """Get a list of lists that contain styling data that can be used by Frame objects"""
        return [r.description for r in self.requirements]

    @classmethod
    def get_requirements_from_json(cls, json) -> list[Requirement]:
        requirements = []
        if 'requirements' in json:
            if type(json['requirements']) != list:
                raise TypeError("requirements field must be a list!")

            for raw_requirement in json['requirements']:
                if 'class' not in raw_requirement:
                    raise ValueError('Bad or missing class field!')

                r = game.structures.loadable_factory.LoadableFactory.get(raw_requirement)  # Instantiate the Requirement via factory
                if not isinstance(r, Requirement):  # Typecheck it
                    raise TypeError(f'Unsupported class {type(r)} found in requirements field!')

                requirements.append(r)

        return requirements


class SkillRequirement(Requirement):
    """
    Fulfilled when the target has a skill level >= the specified level.
    """

    def __init__(self, skill_id: int, level: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skill_id: int = skill_id
        self.level: int = level

        from game.systems.skill import skill_manager
        self._skill_name = skill_manager.get_skill(self.skill_id).name

    def fulfilled(self, entity) -> bool:
        from game.systems.entity.entities import SkillMixin

        if isinstance(entity, SkillMixin):
            return self.skill_id in entity.skill_controller and \
                entity.skill_controller[self.skill_id].level >= self.level

        # If the target entity does not have support for skills (IE, NPC CombatEntities) simply return True
        else:
            return True

    @property
    def description(self) -> list[str | StringContent]:
        return [
            "Requires ",
            StringContent(value=self._skill_name),
            f" level {self.level}"
        ]

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, 'SkillRequirement', LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
                Loads a SkillRequirement object from a JSON blob.

                Required JSON fields:
                - skill_id (int)
                - level (int)
                """

        required_fields = [
            ("skill_id", int), ("level", int)
        ]

        game.structures.loadable_factory.LoadableFactory.validate_fields(required_fields, json)

        return SkillRequirement(json['skill_id'], json['level'])


class ResourceRequirement(Requirement):
    """
    Fulfilled when the target entity has >= the specified quantity of a given resource
    """

    def __init__(self, resource_name: str, adjust_quantity: int | float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_name: str = resource_name
        self.adjust_quantity: int | float = adjust_quantity

    def fulfilled(self, entity) -> bool:
        if type(self.adjust_quantity) == int:  # Resource must be gte adjustment quantity
            if entity.resource_controller[self.resource_name].value < self.adjust_quantity:
                return False

        elif type(self.adjust_quantity) == float:
            _resource = entity.resource_controller[self.resource_name]
            if _resource.remaining_percentage >= self.adjust_quantity:  # Resource % must be >= adjust_quantity
                return False

        else:
            raise TypeError("Adjustment must be of type int or float!")

        return True

    @property
    def description(self) -> list[str | StringContent]:
        sss = f"{self.adjust_quantity}" if type(self.adjust_quantity) == int else f"{self.adjust_quantity * 100}%"
        return [
            "Requires ",
            StringContent(value=sss, formatting="resource_quantity"),
            " of ",
            StringContent(value=self.resource_name, formatting="resource_name")
        ]

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ResourceRequirement", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a ResourceRequirement object from a JSON blob.

        Required JSON fields:
        - resource_name (str)
        - adjust_quantity (float | int)
        """

        required_fields = [('resource_name', str), ('adjust_quantity', Union[int, float])]
        game.structures.loadable_factory.LoadableFactory.validate_fields(required_fields, json)

        if json['class'] != "ResourceRequirement":
            raise ValueError(f"Invalid class field for ResourceRequirement! Got {json['class']} "
                             f"instead of ResourceRequirement!")

        return ResourceRequirement(json['resource_name'], json['adjust_quantity'])


class ConsumeResourceRequirement(Requirement):
    """
    Fulfilled when the specified quantity of a resource is successfully consumed.
    """

    def __init__(self, resource_name: str, adjust_quantity: int | float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_name: str = resource_name
        self.adjust_quantity: int | float = adjust_quantity

    def fulfilled(self, entity) -> bool:
        if type(self.adjust_quantity) == int:  # Resource must be gte adjustment quantity
            if entity.resource_controller[self.resource_name].value < self.adjust_quantity:
                return False

        elif type(self.adjust_quantity) == float:
            _resource = entity.resource_controller[self.resource_name]
            if _resource.remaining_percentage >= self.adjust_quantity:  # Resource % must be >= adjust_quantity
                return False

        else:
            raise TypeError("Adjustment must be of type int or float!")

        entity.resource_controller[self.resource_name].adjust(self.adjust_quantity)
        return True

    @property
    def description(self) -> list[str | StringContent]:
        sss = f"{self.adjust_quantity}" if type(self.adjust_quantity) == int else f"{self.adjust_quantity * 100}%"
        return [
            "Consumes ",
            StringContent(value=sss, formatting="resource_quantity"),
            " of ",
            StringContent(value=self.resource_name, formatting="resource_name")
        ]

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ConsumeResourceRequirement", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a ConsumeResourceRequirement object from a JSON blob.

        Required JSON fields:
        - resource_name (str)
        - adjust_quantity (float | int)
        """

        required_fields = [('resource_name', str), ('adjust_quantity', Union[int, float])]
        game.structures.loadable_factory.LoadableFactory.validate_fields(required_fields, json)

        if json['class'] != "ConsumeResourceRequirement":
            raise ValueError(f"Invalid class field for ConsumeResourceRequirement! Got {json['class']} "
                             f"instead of ConsumeResourceRequirement!")

        return ConsumeResourceRequirement(json['resource_name'], json['adjust_quantity'])


class FlagRequirement(Requirement):
    """
    Fulfilled when the designated flag is set to True.
    """

    def __init__(self, flag_name: str, flag_value: bool, description: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag = flag_name
        self.flag_value = flag_value
        self._description = [description]

    def fulfilled(self, entity) -> bool:
        fm = from_cache("managers.FlagManager")
        return fm.get_flag(self.flag)

    @property
    def description(self) -> list[str | StringContent]:
        return self._description

    @staticmethod
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a FlagRequirement object from a JSON blob.

        Required JSON fields:
        - flag_name (str)
        - flag_value (bool)
        - description (str)
        """

        required_fields = [
            ('flag_name', str),
            ('flag_value', bool),
            ('description', str)
        ]

        game.structures.loadable_factory.LoadableFactory.validate_fields(required_fields)

        return FlagRequirement(json['flag_name'], json['flag_value'], json['description'])


class FactionRequirement(Requirement):
    class Mode(Enum):
        GREATER_THAN_EQUAL_TO = "gte"
        LESS_THAN_EQUAL_TO = "lte"
        EQUAL_TO = "eq"

    def __init__(self, faction_id: int, required_affinity: int, mode: str = "gte", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.faction_id: int = faction_id
        self.required_affinity: int = required_affinity
        self.mode: FactionRequirement.Mode = FactionRequirement.Mode(mode)

    def fulfilled(self, entity) -> bool:
        faction_manager = from_cache("managers.FactionManager")

        if self.mode == self.Mode.GREATER_THAN_EQUAL_TO:
            return faction_manager.get_affinity(self.faction_id) >= self.required_affinity

        elif self.mode == self.Mode.LESS_THAN_EQUAL_TO:
            return faction_manager.get_affinity(self.faction_id) >= self.required_affinity

        elif self.mode == self.Mode.EQUAL_TO:
            return faction_manager.get_affinity(self.faction_id) == self.required_affinity

        else:
            raise ValueError(f"Unknown mode {self.mode}")

    @property
    def description(self) -> list[str | StringContent]:
        faction_manager = from_cache("managers.FactionManager")

        return [
            f"Must have an affinity of at least {self.required_affinity} with the ",
            StringContent(value=faction_manager[self.faction_id].name, formatting="faction_name"),
            "."
        ]

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "FactionRequirement", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a FactionRequirement from a JSON blob.

        Required JSON fields:
        faction_id: (int)
        required_affinity: (int)

        Optional JSON fields:
        mode: (str)
        """

        required_fields = [
            ("faction_id", int),
            ("required_affinity", int)
        ]

        optional_fields = [
            ("mode", str)
        ]

        game.structures.loadable_factory.LoadableFactory.validate_fields(required_fields, json)
        game.structures.loadable_factory.LoadableFactory.validate_fields(optional_fields, json)
        if json['class'] != "FactionRequirement":
            raise ValueError()

        kwargs = {}
        if 'mode' in json:
            kwargs['mode'] = json['mode']

        return FactionRequirement(json['faction_id'], json['required_affinity'], **kwargs)
