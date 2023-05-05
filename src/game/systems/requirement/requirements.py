from abc import ABC

from loguru import logger

from game.structures.loadable import LoadableFactory
from game.structures.messages import StringContent


class Requirement(ABC):
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

    def visit(self, entity) -> None:
        """
        Requirement::visit is an optionally-implement function that performs pre-check logic and spawns any pre-check
        StateDevice objects.

        Args:
        Returns: None
        """
        logger.warning(f"{self.__class__.__name__} has not implemented a visit function!")
        raise RuntimeError()

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

                r = LoadableFactory.get(raw_requirement)  # Instantiate the Requirement via factory
                if not isinstance(r, Requirement):  # Typecheck it
                    raise TypeError(f'Unsupported class {type(r)} found in requirements field!')

                requirements.append(r)

        return requirements


