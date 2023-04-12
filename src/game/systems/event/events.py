import weakref
from abc import ABC
from enum import Enum

from game.structures.enums import InputType
from game.structures.state_device import FiniteStateDevice
import game.systems.currency as currency
import game.util.input_utils
from game.structures.messages import StringContent, ComponentFactory
from game.systems.entity.resource import ResourceController


class Event(FiniteStateDevice, ABC):

    def __init__(self, default_input_type: InputType, states: Enum, default_state):
        super().__init__(default_input_type, states, default_state)


class FlagEvent(Event):
    """An event that sets a specific flag to a given value"""

    class States(Enum):
        DEFAULT = 0

    def __init__(self, flags: [tuple[str, bool]]):
        super().__init__(InputType.SILENT, FlagEvent.States, self.States.DEFAULT)
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
            return ComponentFactory.get()


class AbilityEvent(Event):
    """Causes the player to learn a given ability"""

    class States(Enum):
        DEFAULT = 0
        ALREADY_LEARNED = 1
        NOT_ALREADY_LEARNED = 2
        TERMINATE = 3

    def __init__(self, ability: int):
        super().__init__(InputType.SILENT, AbilityEvent.States, self.States.DEFAULT)
        self.target_ability: int = ability

        @FiniteStateDevice.state_content(instance=self, state=self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

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
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.set_dead()


class CurrencyEvent(Event):
    class States(Enum):
        DEFAULT = 0

    def __init__(self, currency_id: int | str, quantity: int):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
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
    class States(Enum):
        DEFAULT = 0

    def __init__(self, recipe_id: int):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self.recipe_id = recipe_id

    # TODO: Implement RecipeEvent logic
    def _logic(self, _: any) -> None:
        pass

    @property
    def components(self) -> dict[str, any]:
        return {}


class ReputationEvent(Event):
    class States(Enum):
        DEFAULT = 0

    def __init__(self, faction_id: int, reputation_change: int, silent: bool = False):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
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
    class States(Enum):
        DEFAULT = 0
        APPLY = 1
        SUMMARY = 2
        TERMINATE = -1

    def _build_summary(self, start_value: int, end_value: int) -> None:
        """Assemble a list[str | StringContent] to be printed within the SUMMARY state"""
        self._summary = [
            f"{self.target.name} {'lost' if self.amount < 0 else 'gained'}",
            f"{abs(start_value - end_value)} ",
            StringContent(value=f"{self.stat_name}.", formatting="resource_name")
        ]

    def __init__(self, stat_name: str, stat_change: int | float, target, silent: bool = False):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self.stat_name: str = stat_name
        self.amount: int | float = stat_change
        self.target = weakref.proxy(target)  # Weakref to an Entity object
        self._summary: list[str | StringContent] = None
        self._silent = silent

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_):
            from game.systems.entity.entities import Entity  # Import locally to prevent circular import issues

            if not isinstance(self.target, Entity):
                raise TypeError(f"Cannot apply a ResourceEvent to an object of type {self.target}")

            self.set_state(self.States.APPLY)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.APPLY, InputType.SILENT)
        def logic(_):
            resource_controller: ResourceController = self.target.resources
            self._build_summary(resource_controller.resources[self.stat_name].value,                # Current value
                                resource_controller.resources[self.stat_name].adjust(self.amount))  # Post-adjust value
            self.set_state(self.States.SUMMARY)

        @FiniteStateDevice.state_content(self, self.States.APPLY)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.SUMMARY, InputType.SILENT if self._silent else InputType.ANY)
        def logic(_: any):
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.SUMMARY)
        def content():
            return ComponentFactory.get(self._summary)

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.set_dead()

        @FiniteStateDevice.state_content(self, self.States.TERMINATE)
        def content():
            return ComponentFactory.get()
