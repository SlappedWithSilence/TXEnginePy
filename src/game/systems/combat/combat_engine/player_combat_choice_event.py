from enum import Enum

from game.cache import cached, from_cache, from_storage
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice
from game.systems.event import Event
import game.systems.item as items
from game.systems.event.select_item_event import SelectItemEvent


class PlayerCombatChoiceEvent(Event):
    """
    Guides the player through choosing an action to take for a given entity during Combat
    """

    class States(Enum):
        DEFAULT = 0  # Setup
        CHOOSE_TURN_OPTION = 1  # Show the user which options are available
        CHOOSE_AN_ABILITY = 2  # Show the user abilities and request a selection
        CHOOSE_ABILITY_TARGET = 3  # If the ability requires a target, show available targets and request an selection
        CANNOT_USE_ABILITY = 4  # If the ability cannot be user for some reason, say so
        CHOOSE_AN_ITEM = 5  # Show the user all available items and request a selection
        DETECT_ITEM_USABLE = 6  # Check if the user can use the item and go to the appropriate state
        CANNOT_USE_ITEM = 7  # If the item cannot be used for some reason, say so
        SUBMIT_CHOICE = 8  # Once all choices have been finalized, submit them to the global combat instance
        PASS_TURN = 9  # If the choice was to pass, do so
        LIST_ENEMIES = 10  # Show a list of enemies that can be inspected
        LIST_ALLIES = 11  # SHow a list of allies that can be inspected
        INSPECT_ENTITY = 12  # SHow details about a specific entity
        TERMINATE = -1  # Clean up

    def _get_turn_choices(self) -> dict[str, States]:
        return {
            "Inspect enemies": self.States.LIST_ENEMIES,
            "Inspect allies": self.States.LIST_ALLIES,
            "Use an ability": self.States.CHOOSE_AN_ABILITY,
            "Use an item": self.States.CHOOSE_AN_ITEM,
            "Pass turn": self.States.PASS_TURN
        }

    def __init__(self, entity):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self._links: dict[str, dict[str, str]] = {}
        self._entity = entity  # The entity for which to make a choice
        self._choice: str | None = None  # The choice made
        self._available_turn_choices: dict[str, PlayerCombatChoiceEvent.States] = self._get_turn_choices()

        from game.systems.entity.entities import CombatEntity
        if not isinstance(self._entity, CombatEntity):
            raise TypeError(f"Invalid type for field `entity`! Expected CombatEntity, got {type(entity)}")

        self._setup_states()

    def _setup_states(self) -> None:
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            self.set_state(self.States.CHOOSE_TURN_OPTION)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        # SHOW_OPTIONS
        @FiniteStateDevice.state_logic(self, self.States.CHOOSE_TURN_OPTION, InputType.INT,
                                       input_min=0, input_max=len(self._available_turn_choices) - 1)
        def logic(user_input: int) -> None:
            # Convert choice dict into list and fetch which str is related to the index given by the user.
            self._choice = list(self._available_turn_choices.keys())[user_input]
            self.set_state(self._available_turn_choices[self._choice])  # Transition to state mapped to choice

        @FiniteStateDevice.state_content(self, self.States.CHOOSE_TURN_OPTION)
        def content() -> dict:
            return ComponentFactory.get(
                ["What would you like to do?"],
                [[s] for s in self._available_turn_choices.keys()]  # Terrible conversion to satisfy type-checking
            )

        # CHOOSE_AN_ABILITY
        @FiniteStateDevice.state_logic(self, self.States.CHOOSE_AN_ABILITY, InputType.INT)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.CHOOSE_AN_ABILITY)
        def content() -> dict:
            return ComponentFactory.get()

        # CHOOSE_ABILITY_TARGET
        @FiniteStateDevice.state_logic(self, self.States.CHOOSE_ABILITY_TARGET, InputType.INT)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.CHOOSE_ABILITY_TARGET)
        def content() -> dict:
            return ComponentFactory.get()

        # CANNOT_USE_ABILITY
        @FiniteStateDevice.state_logic(self, self.States.CANNOT_USE_ABILITY, InputType.ANY)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.CANNOT_USE_ABILITY)
        def content() -> dict:
            return ComponentFactory.get()

        # CHOOSE_AN_ITEM
        @FiniteStateDevice.state_logic(self, self.States.CHOOSE_AN_ITEM, InputType.SILENT)
        def logic(_: any) -> None:
            from game.systems.item.item import Usable
            select_usable_event = SelectItemEvent(self._entity, lambda item: isinstance(item, Usable))
            self._links['CHOOSE_AN_ITEM'] = select_usable_event.link()

        @FiniteStateDevice.state_content(self, self.States.CHOOSE_AN_ITEM)
        def content() -> dict:
            return ComponentFactory.get()

        # DETECT_ITEM_USABLE
        @FiniteStateDevice.state_logic(self, self.States.DETECT_ITEM_USABLE, InputType.SILENT)
        def logic(_: any) -> None:
            chosen_item_id = from_storage(self._links["CHOOSE_AN_ITEM"]['selected_item_id'])

            if chosen_item_id is None:
                self.set_state(self.States.SHOW_OPTIONS)
                return

        @FiniteStateDevice.state_content(self, self.States.DETECT_ITEM_USABLE)
        def content():
            return ComponentFactory.get()

        # CANNOT_USE_ITEM
        @FiniteStateDevice.state_logic(self, self.States.CANNOT_USE_ITEM, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.CHOOSE_AN_ITEM)

        @FiniteStateDevice.state_content(self, self.States.CANNOT_USE_ITEM)
        def content() -> dict:
            item_instance = from_cache('managers.ItemManager').get_instance(self._choice)

            return ComponentFactory.get(
                [
                    f"You cannot use ",
                    StringContent(value=item_instance.name, formatting="item_name"),
                    "!"
                ],
                item_instance.get_requirements_as_options()
            )

        # SUBMIT_CHOICE
        @FiniteStateDevice.state_logic(self, self.States.SUBMIT_CHOICE, InputType.SILENT)
        def logic(_: any) -> None:
            from_cache("combat").submit_entity_choice(self._entity, self._choice)
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.SUBMIT_CHOICE)
        def content() -> dict:
            return ComponentFactory.get()

        # PASS_TURN
        @FiniteStateDevice.state_logic(self, self.States.PASS_TURN, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.SUBMIT_CHOICE)

        @FiniteStateDevice.state_content(self, self.States.PASS_TURN)
        def content() -> dict:
            return ComponentFactory.get(
                [StringContent(value=self._entity.name, formatting="entity_name"), " chose not to act."]
            )

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "PlayerCombatChoiceEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        raise RuntimeError("Loading of PlayerCombatChoiceEvent from JSON is not supported!")
