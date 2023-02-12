from ...structures.enums import InputType, affirmative_to_bool
from ...structures.messages import StringContent
from ...structures.state_device import StateDevice
from ...formatting import get_style
from ..currency import currency_manager

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
    already_learned_message = [StringContent(value="You already learned "),
                               StringContent(value="LOOK UP ABILITY NAME", formatting=get_style("ability_name"))
                               ]

    def __init__(self, ability: int):
        super().__init__(input_type=InputType.NONE)
        self.target_ability: int = ability

    @property
    def components(self) -> dict[str, any]:
        return {"content": self.learn_message}  # TODO: Implement already-learned message

    # TODO: Implement AbilityEvent logic
    def _logic(self, _) -> None:
        """
        Check if the ability has been learned. If it hasn't been learned, learn it
        """
        # Check if player has ability
        # if so, set text to reflect redundant learning
        # if not, learn the ability
        # TODO: Implement


class ItemEvent(Event):
    """
    Asks the player if they want to accept 'n' of an item. If they do, spawn an item-handling StateDevice
    """

    def __init__(self, item_id: int, quantity: int):
        super().__init__(input_type=InputType.AFFIRMATIVE)
        self.item_id = item_id
        self.quantity = quantity

    def _logic(self, user_input: str) -> None:
        # TODO: Implement
        if affirmative_to_bool(user_input):
            # Spawn item-acquisition StateDevice
            pass

    @property
    def components(self) -> dict[str, any]:
        # TODO: Implement translate item.id to item.name
        return {"content": [StringContent(value="You've found"),
                            StringContent(value=str(self.quantity), formatting=get_style("item_quantity")),
                            StringContent(value=" of "),
                            StringContent(value=f"item::{self.item_id}", formatting=get_style("item_name")),
                            StringContent(value=". Do you want to add it to your inventory?")
                            ]
                }


class CurrencyEvent(Event):

    def __init__(self, currency_id: int | str, quantity: int):
        super().__init__(input_type=InputType.NONE)
        self.currency_id = currency_id
        self.quantity = quantity
        self.cur = currency_manager.to_currency(currency_id, abs(quantity))
        self.gain_message: list[StringContent] = [
            StringContent(value="You gained "),
            StringContent(value=str(self.cur))
        ]
        self.loss_message: list[StringContent] = [
            StringContent(value="You lost "),
            StringContent(value=str(self.cur))
        ]

    # TODO: Implement MoneyEvent logic
    def _logic(self, _: any) -> None:
        # If quantity > 0, set gain message
        # If quantity < 0 set loss message
        # Set currency
        pass

    @property
    def components(self) -> dict[str, any]:
        if self.quantity < 0:
            msg = self.loss_message
        else:
            msg = self.gain_message

        return {"content": msg}


class RecipeEvent(Event):

    def __init__(self, recipe_id: int):
        super().__init__(input_type=InputType.NONE)
        self.recipe_id = recipe_id

    # TODO: Implement RecipeEvent logic
    def _logic(self, _: any) -> None:
        pass


class ReputationEvent(Event):

    def __init__(self, faction_id: int, reputation_change: int, silent: bool = False):
        super().__init__(input_type=InputType.SILENT if silent else InputType.NONE)
        self.faction_id = faction_id
        self.reputation_change = reputation_change
        self.message = [StringContent(value="Your reputation with "),
                        StringContent(value=f"faction::{faction_id}", formatting=get_style("faction_name")),
                        StringContent(value="decreased" if self.reputation_change < 0 else "increased"),
                        StringContent(value=f" by {reputation_change}")
                        ]

    # TODO: Implement ReputationEvent logic
    def _logic(self, _: any) -> None:
        # Parse properties[1] into growth-change enum
        # parse properties[2] into growth-mode enum
        # Calculate total rep change
        # Apply rep change
        # Set text
        pass

    @property
    def components(self) -> dict[str, any]:
        return {"content": self.message}


class StatEvent(Event):

    def __init__(self, stat_name: str, stat_change: int | float):
        super().__init__(input_type=InputType.NONE)
        self.stat_name = stat_name
        self.stat_name: int | float = stat_change

    def _logic(self, _: any) -> None:
        pass

    @property
    def components(self) -> dict[str, any]:
        pass
