import weakref
from abc import ABC
from enum import Enum

from game.cache import get_cache
from game.structures.enums import InputType
from game.structures.state_device import FiniteStateDevice
import game.systems.currency as currency
import game.systems.flag as flag
import game.util.input_utils
from game.structures.messages import StringContent, ComponentFactory
import game.systems.entity.entities as entities
from game.systems.entity.resource import ResourceController


class Event(FiniteStateDevice, ABC):

    def __init__(self, default_input_type: InputType, states: Enum, default_state):
        super().__init__(default_input_type, states, default_state)


class FlagEvent(Event):
    """ An event that sets a specific flag to a given value

        TXEngine Flags are slightly different from exact str-bool mappings. A Flag may define itself to be a part of a
        flag "subgroup" using dot-notation.
        For example:
         - A flag with a key of some.flag = True would store itself in the flags cache as flags['some']['flag'] = True
         - A flag with a key of this.is.a.deep.flag = False would be flags['this']['is']['a']['deep']['flag'] = False
    """

    def __init__(self, flags: list[tuple[str, bool]]):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self._flags = flags  # The flags to set and their corresponding values

        @FiniteStateDevice.state_logic(input_type=InputType.SILENT, instance=self, state=self.States.DEFAULT)
        def logic(_: any) -> None:
            """
            Perform some logic for setting flags
            """
            for f in self._flags:
                flag.flag_manager.set_flag(*f)

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

    def __init__(self, currency_id: int | str, quantity: int):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self._currency_id = currency_id
        self._quantity = quantity
        self._cur = currency.currency_manager.to_currency(currency_id, quantity)
        self._gain_message: list[StringContent] = [
            StringContent(value="You gained "),
            StringContent(value=str(self._cur))
        ]
        self._loss_message: list[StringContent] = [
            StringContent(value="You lost "),
            StringContent(value=str(self._cur))
        ]

        self._message = self._gain_message if quantity >= 0 else self._loss_message

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.ANY)
        def logic(_: any) -> None:
            player_ref: entities.Player = get_cache()['player']
            player_ref.coin_purse.adjust(self._currency_id, self._quantity)
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get(self._message)


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
            self._build_summary(resource_controller.resources[self.stat_name].value,  # Current value
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
