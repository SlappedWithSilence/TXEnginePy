import game.structures.enums as enums
import game.structures.messages as messages
import game.structures.state_device as state_device
import game.formatting as formatting
import game.systems.currency as currency

from abc import ABC


class Event(state_device.StateDevice, ABC):

    def __init__(self, input_type: enums.InputType):
        super().__init__(input_type)


class FlagEvent(Event):
    """An event that sets a specific flag to a given value"""

    def __init__(self, flags: [tuple[str, bool]]):
        super().__init__(input_type=enums.InputType.NONE)
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

    def __init__(self, ability: int):
        super().__init__(input_type=enums.InputType.NONE)
        self.target_ability: int = ability

    @property
    def components(self) -> dict[str, any]:
        learn_message = [messages.StringContent(value="You learned a new ability!"),
                         messages.StringContent(value="LOOK UP ABILITY NAME",
                                                formatting="ability_name")
                         ]
        already_learned_message = [messages.StringContent(value="You already learned "),
                                   messages.StringContent(value="LOOK UP ABILITY NAME",
                                                          formatting="ability_name")
                                   ]

        return {"content": learn_message}  # TODO: Implement already-learned message

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
        super().__init__(input_type=enums.InputType.AFFIRMATIVE)
        self.item_id = item_id
        self.quantity = quantity

    def _logic(self, user_input: str) -> None:
        # TODO: Implement
        if enums.affirmative_to_bool(user_input):
            # Spawn item-acquisition StateDevice
            pass

    @property
    def components(self) -> dict[str, any]:
        # TODO: Implement translate item.id to item.name
        return {"content": [messages.StringContent(value="You've found"),
                            messages.StringContent(value=str(self.quantity),
                                                   formatting="item_quantity"),
                            messages.StringContent(value=" of "),
                            messages.StringContent(value=f"item::{self.item_id}",
                                                   formatting="item_name"),
                            messages.StringContent(value=". Do you want to add it to your inventory?")
                            ]
                }


class CurrencyEvent(Event):

    def __init__(self, currency_id: int | str, quantity: int):
        super().__init__(input_type=enums.InputType.NONE)
        self.currency_id = currency_id
        self.quantity = quantity
        self.cur = currency.currency_manager.to_currency(currency_id, abs(quantity))
        self.gain_message: list[messages.StringContent] = [
            messages.StringContent(value="You gained "),
            messages.StringContent(value=str(self.cur))
        ]
        self.loss_message: list[messages.StringContent] = [
            messages.StringContent(value="You lost "),
            messages.StringContent(value=str(self.cur))
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
        super().__init__(input_type=enums.InputType.NONE)
        self.recipe_id = recipe_id

    # TODO: Implement RecipeEvent logic
    def _logic(self, _: any) -> None:
        pass

    @property
    def components(self) -> dict[str, any]:
        return {}


class ReputationEvent(Event):

    def __init__(self, faction_id: int, reputation_change: int, silent: bool = False):
        super().__init__(input_type=enums.InputType.SILENT if silent else enums.InputType.NONE)
        self.faction_id = faction_id
        self.reputation_change = reputation_change
        self.message = [messages.StringContent(value="Your reputation with "),
                        messages.StringContent(value=f"faction::{faction_id}",
                                               formatting="faction_name"),
                        messages.StringContent(value="decreased" if self.reputation_change < 0 else "increased"),
                        messages.StringContent(value=f" by {reputation_change}")
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


class ResourceEvent(Event):

    def __init__(self, stat_name: str, stat_change: int | float):
        super().__init__(input_type=enums.InputType.NONE)
        self.stat_name = stat_name
        self.stat_name: int | float = stat_change

    def _logic(self, _: any) -> None:
        pass

    @property
    def components(self) -> dict[str, any]:
        return {}
