import weakref
from abc import ABC
from enum import Enum

from game.structures.enums import InputType
from game.structures.state_device import FiniteStateDevice
import game.systems.currency as currency
import game.util.input_utils
from game import cache
from game.structures.messages import StringContent, ComponentFactory
import game.systems.entity.entities as entities
import game.systems.item as item


class Event(FiniteStateDevice, ABC):

    def __init__(self, default_input_type: InputType, states: Enum):
        super().__init__(default_input_type, states)


class FlagEvent(Event):
    """An event that sets a specific flag to a given value"""

    class States(Enum):
        DEFAULT = 0

    def __init__(self, flags: [tuple[str, bool]]):
        super().__init__(default_input_type=InputType.SILENT, states=FlagEvent.States)
        self.flags = flags  # The flags to set and their corresponding values
        self.current_state = self.States.DEFAULT

        @FiniteStateDevice.state_logic(input_type=InputType.SILENT, instance=self, state=self.States.DEFAULT)
        def logic(user_input: any) -> None:
            """
            Perform some logic for setting flags
            """
            pass

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get([""])


class AbilityEvent(Event):
    """Causes the player to learn a given ability"""

    class States(Enum):
        DEFAULT = 0
        ALREADY_LEARNED = 1
        NOT_ALREADY_LEARNED = 2
        TERMINATE = 3

    def __init__(self, ability: int):
        super().__init__(default_input_type=InputType.SILENT, states=AbilityEvent.States)
        self.target_ability: int = ability

        @FiniteStateDevice.state_content(instance=self, state=self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get([""])

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            check_for_learned = False  # TODO: Implement
            if check_for_learned:
                self.set_state(self.States.ALREADY_LEARNED)
            else:
                self.set_state(self.States.NOT_ALREADY_LEARNED)

        @FiniteStateDevice.state_content(self, self.States.NOT_ALREADY_LEARNED)
        def content() -> dict:
            learn_message = [StringContent(value="You learned a new ability!"),
                             StringContent(value="LOOK UP ABILITY NAME",
                                           formatting="ability_name")]
            return ComponentFactory.get(learn_message)

        @FiniteStateDevice.state_logic(self, self.States.NOT_ALREADY_LEARNED, InputType.NONE)
        def logic(_: any) -> None:
            # TODO: Implement ability learning method
            print("LEARN AN ABILITY")

            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.ALREADY_LEARNED)
        def content() -> dict:
            already_learned_message = [StringContent(value="You already learned "),
                                       StringContent(value="LOOK UP ABILITY NAME",
                                                     formatting="ability_name")
                                       ]
            return ComponentFactory.get(already_learned_message)

        @FiniteStateDevice.state_logic(self, self.States.ALREADY_LEARNED, input_type=InputType.NONE)
        def logic(_: any):
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.TERMINATE)
        def content() -> dict:
            return ComponentFactory.get([""])

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.set_dead()


class AddItemEvent(Event):
    """
    An Event that flows the user through the process of adding an item to their inventory.

    This is usually an automatic process, but occasionally requires user intervention, particularly when there isn't
    enough inventory space.
    """

    class States(Enum):
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
        INSERT_ITEM = 1
        PROMPT_KEEP_NEW_ITEM = 2

    def __init__(self, item_id: int, item_quantity: int = 1):
        super().__init__(InputType.SILENT, AddItemEvent.States)
        self.item_id = item_id
        self.item_quantity = item_quantity
        self.state = self.State.ITEM_ADDED
        self.player_ref: entities.Player = weakref.proxy(cache.get_cache()['player'])





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
        super().__init__(input_type=InputType.NONE)
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
        super().__init__(input_type=InputType.NONE)
        self.recipe_id = recipe_id

    # TODO: Implement RecipeEvent logic
    def _logic(self, _: any) -> None:
        pass

    @property
    def components(self) -> dict[str, any]:
        return {}


class ReputationEvent(Event):

    def __init__(self, faction_id: int, reputation_change: int, silent: bool = False):
        super().__init__(input_type=InputType.SILENT if silent else InputType.NONE)
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
        super().__init__(input_type=InputType.NONE)
        self.stat_name = stat_name
        self.stat_name: int | float = stat_change

    def _logic(self, _: any) -> None:
        pass

    @property
    def components(self) -> dict[str, any]:
        return {}
