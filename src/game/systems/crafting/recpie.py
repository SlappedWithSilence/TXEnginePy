from abc import ABC

from game.cache import cached
from game.structures.loadable import LoadableMixin, LoadableFactory
from game.systems.requirement.requirements import RequirementsMixin


class RecipeBase(ABC):
    """Base class for Recipe objects that defines class-specific properties"""

    def __init__(self, recipe_id: int, items_in: list[tuple[int, int]], items_out: list[tuple[int, int]]):
        self.id = recipe_id
        self.items_in: list[tuple[int, int]] = items_in  # Items that are consumed to perform the recipe
        self.items_out: list[tuple[int, int]] = items_out  # Items returned to the user after performing the recipe


class Recipe(LoadableMixin, RequirementsMixin, RecipeBase):
    """Proper class for Recipe objects. Inherits from multiple mixins."""

    def __init__(self, id: int, items_in: list[tuple[int, int]], items_out: list[tuple[int, int]], **kwargs):
        super().__init__(recipe_id=id, items_in=items_in, items_out=items_out, **kwargs)

    @staticmethod
    @cached
    def from_json(json: dict[str, any]) -> any:
        """
        Instantiate a Recipe object from a JSON blob.

        Args:
            json: a dict-form representation of a json object

        Returns: a Recipe instance with the properties defined in the JSON

        Required JSON fields:
        - id (int)
        - items_in: [[int, int]]
        - items_out: [[int, int]]

        Optional attribute fields:
        - requirements: [Requirement]

        Optional JSON fields:
        - None
        """

        required_fields = [("id", int), ("items_in", list), ("items_out", list)]
        LoadableFactory.validate_required_fields(required_fields, json)

        requirements: list = RequirementsMixin.get_requirements_from_json(json) if 'requirements' in json else []

        return Recipe(json['id'],
                      json['items_in'],
                      json['items_out'],
                      requirements=requirements)
