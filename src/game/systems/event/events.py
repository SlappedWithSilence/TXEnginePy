from ...structures.enums import InputType
from ...structures.messages import StringContent
from ...structures.state_device import StateDevice
from ...formatting import get_style

from abc import ABC
from typing import Union, Any


class Event(StateDevice, ABC):

    def __init__(self, input_type: InputType):
        super().__init__(input_type)


class FlagEvent(Event):
    """An event that sets a specific flag to a given value"""

    def __init__(self, flags: [tuple[str, bool]]):

        super().__init__(input_type=InputType.NONE)
        self.flags = flags  # The flags to set and their corresponding values

    @property
    def components(self) -> dict[str, any]:
        return {}

    def _logic(self, _: any) -> None:

        for flag in self.flags:
            # TODO: Implement flag setter
            pass


class AbilityEvent(Event):
    """Causes the player to learn a given ability"""

    learn_message = [StringContent(value="You learned a new ability!"),
                     StringContent(value="LOOK UP ABILITY NAME", formatting=get_style("ability_name"))
                     ]

    def __init__(self, ability: int):
        super().__init__(input_type=InputType.NONE)
        self.target_ability: int = ability

    @property
    def components(self) -> dict[str, any]:

        return {}

    # TODO: Implement AbilityEvent logic
    def _logic(self, _) -> None:
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


class ReputationEvent(Event):

    def __init__(self, properties: list[str]):
        super().__init__(properties)

        if len(properties) != 3:
            raise ValueError(f"RecipeEvent must have exactly three properties! Got {len(properties)}")

    # TODO: Implement ReputationEvent logic
    def logic(self) -> None:
        self._faction_name = self._properties[0]
        # Parse properties[1] into growth-change enum
        # parse properties[2] into growth-mode enum
        # Calculate total rep change
        # Apply rep change
        # Set text
        pass


class StatEvent(Event):

    def __init__(self, properties: list[str]):
        super().__init__(properties)

        if len(properties) != 2:
            raise ValueError(f"StatEvent must have exactly two properties! Got {len(properties)}")

    def logic(self) -> None:
        stat_name = self._properties[0]
        stat_change: Union[int, float] = None

        # Try to parse data
        try:
            stat_change = int(self._properties[1])  # int?

        except TypeError:
            pass  # Apparently not

        if not stat_change:
            stat_change = float(self._properties[1])  # float?

        if stat_name not in player.stats:  # Verify stat exists
            raise ValueError(f"Stat '{stat_name}' does not exist!")

        if not stat_change:
            raise TypeError("StatEvent's properties must be typed [str, int|float]!")  # still no, something's wrong

        player.stats[stat_name].adjust(stat_change, verbose=True)
