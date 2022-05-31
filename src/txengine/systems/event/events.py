from ..flag import flags
from ...ui.color import style
from ..item.item_util import item_name

from abc import ABC
from typing import Union

from rich import print


class Event(ABC):

    def __init__(self, properties: list[str], text: Union[str, None] = None):
        self._properties: list[str] = properties
        self._text: Union[str, None] = text

    def logic(self) -> None:
        """Core logic for the Event"""
        pass

    def perform(self) -> None:
        """Wrapper for logic that prints optional user prompting"""
        if self._text:
            print(self._text)
        self.logic()


class FlagEvent(Event):
    """An event that sets a specific flag to a given value"""

    def __init__(self, properties: list[str]):
        super().__init__(properties)
        if len(properties) != 2:
            raise ValueError(f"FlagEvents must have exactly two properties! Got {len(properties)}")

    def logic(self) -> None:

        try:
            flag_value = bool(self._properties)
            flags[self._properties[0]] = flag_value

        except TypeError:  # Any exception from type conversion is really a value error from the JSON files
            raise ValueError("FlagEvent's properties must be typed [str, bool]!")


class AbilityEvent(Event):
    """Causes the player to learn a given ability"""

    def __init__(self, properties: list[str]):
        super().__init__(properties)
        self._text = style("You learned a new ability: ", "player_improvement") + style(properties[0], "ability")

        if len(properties) != 1:
            raise ValueError(f"AbilityEvent must have exactly one property! Got {len(properties)}")

    # TODO: Implement AbilityEvent logic
    def logic(self) -> None:
        # Check if player has ability
        # if so, set text to reflect redundant learning
        # if not, learn the ability
        pass


class ItemEvent(Event):
    """Causes the player to obtain 'n' of a given item"""

    def __init__(self, properties: list[str]):
        super().__init__(properties)

        if len(properties) != 2:
            raise ValueError(f"ItemEvent must have exactly two properties! Got {len(properties)}")

        try:
            self._item_id = int(self._properties[0])
            self._item_quantity = int(self._properties[1])

        except TypeError:
            raise ValueError("ItemEvent's properties must be typed [int, int]!")

        self._text = style(f"You obtained {self._item_quantity} ", "player_improvement") + \
                     style(item_name(self._item_id), "item")

    # TODO: Implement ItemEvent logic
    def logic(self) -> None:
        # Get player's inventory
        # call add_item
        pass


class MoneyEvent(Event):

    def __init__(self, properties: list[str]):
        super().__init__(properties)

        if len(properties) != 1:
            raise ValueError(f"MoneyEvent must have exactly one property! Got {len(properties)}")

    # TODO: Implement MoneyEvent logic
    def logic(self) -> None:
        # If quantity > 0, set gain message
        # If quantity < 0 set loss message
        # Set currency
        pass


class RecipeEvent(Event):

    def __init__(self, properties: list[str]):
        super().__init__(properties)

        if len(properties) != 1:
            raise ValueError(f"RecipeEvent must have exactly one property! Got {len(properties)}")

        self._text = style("You learned a new recipe!", "player_improvement")

    # TODO: Implement RecipeEvent logic
    def logic(self) -> None:
        # Add given recipe to learned recipes
        try:
            recipe_id = int(self._properties[0])

        except TypeError:
            raise ValueError("RecipeEvent's properties must be typed [int]!")
