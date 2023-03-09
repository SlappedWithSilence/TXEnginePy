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
from game.systems.item.item import Usable


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

        @FiniteStateDevice.state_logic(self, self.States.NOT_ALREADY_LEARNED, InputType.ANY)
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

        @FiniteStateDevice.state_logic(self, self.States.ALREADY_LEARNED, input_type=InputType.ANY)
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
        DEFAULT = 0
        PROMPT_KEEP_NEW_ITEM = 1
        INSERT_ITEM = 2
        TERMINATE = -1

    def __init__(self, item_id: int, item_quantity: int = 1):
        """
        Args:
            item_id: The ID of the Item to attempt to add to the player's inventory.
            item_quantity: The quantity of the Item to attemtp to add to the player's inventory.

        Returns: An instance of an AddItemEvent
        """
        super().__init__(InputType.SILENT, AddItemEvent.States)
        self.item_id = item_id
        self.item_quantity = item_quantity
        self.remaining_quantity = item_quantity
        self.current_state = self.States.DEFAULT  # Set the starting state to DEFAULT
        self.player_ref: entities.Player = weakref.proxy(cache.get_cache()['player'])  # Grab a weak reference to Player
        self._build_states()

    def _build_states(self) -> None:
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            # Detect collision
            if self.player_ref.inventory.is_collidable(self.item_id, self.remaining_quantity):
                self.set_state(self.States.PROMPT_KEEP_NEW_ITEM)  # Make player choose to keep or drop new item
            else:
                self.set_state(self.States.INSERT_ITEM)  # Insert items

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get([""])

        @FiniteStateDevice.state_logic(self, self.States.PROMPT_KEEP_NEW_ITEM, InputType.AFFIRMATIVE)
        def logic(user_input: bool) -> None:
            if user_input:
                self.set_state(self.States.INSERT_ITEM)
            else:
                self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.PROMPT_KEEP_NEW_ITEM)
        def content() -> dict:
            c = ["Would you like to make room in your inventory for ",
                 StringContent(value=f"{self.remaining_quantity}x ", formatting="item_quantity"),
                 StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                 "?"
                 ]
            return ComponentFactory.get(c)

        @FiniteStateDevice.state_logic(self, self.States.INSERT_ITEM, InputType.ANY)
        def logic(_: any) -> None:
            self.remaining_quantity = self.player_ref.inventory.insert_item(self.item_id, self.item_quantity)

            if self.remaining_quantity > 0:
                self.set_state(self.States.PROMPT_KEEP_NEW_ITEM)
            else:
                self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.INSERT_ITEM)
        def content() -> dict:
            return ComponentFactory.get(
                [
                    f"You added ",
                    StringContent(value=str(self.item_quantity), formatting="item_quantity"),
                    "x ",
                    StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                    " to your inventory."
                ]
            )

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.set_dead()

        @FiniteStateDevice.state_content(self, self.States.TERMINATE)
        def content() -> dict:
            return ComponentFactory.get([])


class CurrencyEvent(Event):

    def __init__(self, currency_id: int | str, quantity: int):
        super().__init__(input_type=InputType.ANY)
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
        super().__init__(input_type=InputType.ANY)
        self.recipe_id = recipe_id

    # TODO: Implement RecipeEvent logic
    def _logic(self, _: any) -> None:
        pass

    @property
    def components(self) -> dict[str, any]:
        return {}


class ReputationEvent(Event):

    def __init__(self, faction_id: int, reputation_change: int, silent: bool = False):
        super().__init__(input_type=InputType.SILENT if silent else InputType.ANY)
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
        super().__init__(input_type=InputType.ANY)
        self.stat_name = stat_name
        self.stat_name: int | float = stat_change

    def _logic(self, _: any) -> None:
        pass

    @property
    def components(self) -> dict[str, any]:
        return {}


class UseItemEvent(Event):
    class States(Enum):
        DEFAULT = 0
        USE_ITEM = 1
        NOT_USABLE = 2
        NOT_REQUIREMENTS = 3
        TERMINATE = -1

    def __init__(self, stack_index: int):
        super().__init__(InputType.SILENT, UseItemEvent.States)
        self.stack_index = stack_index
        self.player_ref: entities.Player = cache.get_cache()['player']

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            if isinstance(self.player_ref.inventory.items[self.stack_index].ref, Usable):

                if self.player_ref.inventory.items[self.stack_index].ref.is_requirements_fulfilled():
                    self.set_state(self.States.USE_ITEM)
                else:
                    self.set_state(self.States.NOT_REQUIREMENTS)

            else:
                self.set_state(self.States.NOT_USABLE)
