import weakref
from abc import ABC
from enum import Enum

import game.structures.enums as enums
import game.structures.state_device as state_device
import game.systems.currency as currency
import game.util.input_utils
from game import cache
from game.structures.messages import StringContent, ComponentFactory
import game.systems.entity.entities as entities
import game.systems.item as item


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
        learn_message = [StringContent(value="You learned a new ability!"),
                         StringContent(value="LOOK UP ABILITY NAME",
                                                formatting="ability_name")
                         ]
        already_learned_message = [StringContent(value="You already learned "),
                                   StringContent(value="LOOK UP ABILITY NAME",
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


class AddItemEvent(Event):
    """
    An Event that flows the user through the process of adding an item to their inventory.

    This is usually an automatic process, but occasionally requires user intervention, particularly when there isn't
    enough inventory space.
    """

    class EventState(Enum):
        """
        Case 1: item already in inventory
        Case 1a: non-full stack exists
        Case 1a.a add items into non-full stack.
        Case 1a.a.a: Overflow--call add_item on overflowing quantity recursively
        Case 1a.a.b: No overflow--terminate
        Case 1b: only full stacks exists
        Case 1b.a: Inventory not full: Create a stack. If overflow, call add_item on overflowing quantity recursively
        Case 1b.b: Inventory full--Prompt user to make space, call add_item again
        Case 2: item not in inventory
        Case 2.a: inventory not full--create new stack
        Case 2.a.a: overflow-- call add_item recursively on overflowing quantity
        Case 2.a.b: no overflow--terminate
        Case  2.b: inventory full--prompt user to make space, call add_item again
        """

        DEFAULT = 0
        PROMPT_REMOVE_STACK = 1,
        CONFIRM_REMOVE_STACK = 2,
        REFUSE_REMOVE_STACK = 3,
        CONFIRM_REFUSE_REMOVE_STACK = 4,
        ITEM_ADDED = 5,
        SELECT_STACK = 6,
        TERMINATE = 8

    def __init__(self, item_id: int, item_quantity: int = 1):
        super().__init__(input_type=enums.InputType.SILENT)
        self.item_id = item_id
        self.item_quantity = item_quantity
        self.state = self.EventState.ITEM_ADDED
        self.player_ref: entities.Player = weakref.proxy(cache.get_cache()['player'])

    def _requires_user_intervention(self) -> bool:
        """
        A function that computes whether the user is needed to resolve a collision or overflow within the inventory as
        a result of the Event.

        Args:

        Returns: True if the user is required to resolve a collision, False otherwise
        """

    @property
    def components(self) -> dict[str, any]:

        if self.state == self.EventState.DEFAULT:

            return ComponentFactory.get([""])

        elif self.state == self.EventState.PROMPT_REMOVE_STACK:
            c = ["Your inventory has insufficient free space to add ",
                 StringContent(value=f"{self.item_quantity}x", format="item_quantity"),
                 " ",
                 StringContent(value=f"{item.item_manager.get_name(self.item_id)}", format="item_name"),
                 ". Do you wish to drop a stack of items to make room in your inventory?"]
            return ComponentFactory.get(c)

        elif self.state == self.EventState.SELECT_STACK:
            c = ["Which stack would you like to drop to make room?"]
            return ComponentFactory.get(c, self.player_ref.inventory.to_options())

        elif self.state == self.EventState.CONFIRM_REMOVE_STACK:
            c = ["Are you sure you want to drop this stack?"]
            return ComponentFactory.get(c)

        elif self.state == self.EventState.ITEM_ADDED:
            c = ["You added ",
                 StringContent(value=item.item_manager.get_name(self.item_id), formatting="item_name"),
                 StringContent(value=f" {self.item_quantity}x ", formatting="item_quantity"),
                 "to your inventory."]
            return ComponentFactory.get(c)

        elif self.state == self.EventState.REFUSE_REMOVE_STACK:
            c = ["You dropped the items on the floor."]
            return ComponentFactory.get(c)

        elif self.state == self.EventState.CONFIRM_REFUSE_REMOVE_STACK:
            c = ["Are you sure you want to drop ",
                 StringContent(value=item.item_manager.get_name(self.item_id), formatting="item_name"),
                 StringContent(value=f" {self.item_quantity}x", formatting="item_quantity"),
                 "?"
                 ]
            return ComponentFactory.get(c)

        elif self.state == self.EventState.TERMINATE:
            return ComponentFactory.get([])

    def _logic(self, user_input: any) -> None:

        # Default State
        if self.state == self.EventState.DEFAULT:

            # If the player needs to intervene, silently set state to PROMPT REMOVE STACK
            if self.player_ref.inventory.is_collidable(self.item_id, self.item_quantity):
                self.state = self.EventState.PROMPT_REMOVE_STACK
                self.input_type = enums.InputType.AFFIRMATIVE

            # If the player doesn't need to intervene, simply execute the item add
            else:
                self.state = self.EventState.ITEM_ADDED
                self.input_type = enums.InputType.NONE

        elif self.state == self.EventState.PROMPT_REMOVE_STACK:
            if user_input:
                self.state = self.EventState.SELECT_STACK
                self.input_type = enums.InputType.INT
                self.domain_min = 0
                self.domain_max = len(self.player_ref.inventory.items)
            else:
                self.state = self.EventState.CONFIRM_REFUSE_REMOVE_STACK
                self.input_type = enums.InputType.AFFIRMATIVE

        elif self.state == self.EventState.REFUSE_REMOVE_STACK:
            self.state = self.EventState.TERMINATE
            self.input_type = enums.InputType.SILENT

        elif self.state == self.EventState.TERMINATE:
            import game
            game.state_device_controller.set_dead()

        elif self.state == self.EventState.SELECT_STACK:
            self.player_ref.inventory.drop_stack(user_input)

            if self.player_ref.inventory.is_collidable(self.item_id, self.item_quantity):
                self.state = self.EventState.SELECT_STACK
                self.input_type = enums.InputType.INT
                self.domain_min = 0
                self.domain_max = len(self.player_ref.inventory.items)



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
        if game.util.input_utils.affirmative_to_bool(user_input):
            # Spawn item-acquisition StateDevice
            pass

    @property
    def components(self) -> dict[str, any]:
        # TODO: Implement translate item.id to item.name
        return {"content": [StringContent(value="You've found"),
                            StringContent(value=str(self.quantity),
                                                   formatting="item_quantity"),
                            StringContent(value=" of "),
                            StringContent(value=f"item::{self.item_id}",
                                                   formatting="item_name"),
                            StringContent(value=". Do you want to add it to your inventory?")
                            ]
                }


class CurrencyEvent(Event):

    def __init__(self, currency_id: int | str, quantity: int):
        super().__init__(input_type=enums.InputType.NONE)
        self.currency_id = currency_id
        self.quantity = quantity
        self.cur = currency.currency_manager.to_currency(currency_id, abs(quantity))
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
        self.message = [StringContent(value="Your reputation with "),
                        StringContent(value=f"faction::{faction_id}",
                                               formatting="faction_name"),
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
