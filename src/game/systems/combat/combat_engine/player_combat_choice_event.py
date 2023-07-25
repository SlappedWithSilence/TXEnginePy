from enum import Enum

from game.cache import cached, from_cache
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice
from game.systems.event import Event
import game.systems.item as items


class PlayerCombatChoiceEvent(Event):
    """
    Guides the player through choosing an action to take for a given entity during Combat
    """

    class States(Enum):
        DEFAULT = 0  # Setup
        SHOW_OPTIONS = 1  # Show the user which options are availbale
        CHOOSE_AN_ABILITY = 2  # Show the user abilities and request a selection
        CHOOSE_ABILITY_TARGET = 3  # If the ability requires a target, show available targets and request an selection
        CANNOT_USE_ABILITY = 4  # If the ability cannot be user for some reason, say so
        CHOOSE_AN_ITEM = 5  # Show the user all available items and request a selection
        CANNOT_USE_ITEM = 6  # If the item cannot be used for some reason, say so
        SUBMIT_CHOICE = 7  # Once all choices have been finalized, submit them to the global combat instance
        PASS_TURN = 8  # If the choice was to pass, do so
        TERMINATE = -1  # Clean up

    def __init__(self, entity):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self._entity = entity  # The entity for which to make a choice
        self._choice: int | str | None = None  # The choice made

        from game.systems.entity.entities import CombatEntity
        if not isinstance(self._entity, CombatEntity):
            raise TypeError(f"Invalid type for field `entity`! Expected CombatEntity, got {type(entity)}")

        self._setup_states()

    def _setup_states(self) -> None:
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            self.set_state(self.States.SHOW_OPTIONS)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        # SHOW_OPTIONS
        @FiniteStateDevice.state_logic(self, self.States.SHOW_OPTIONS, InputType.INT)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.SHOW_OPTIONS)
        def content() -> dict:
            return ComponentFactory.get()

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
        @FiniteStateDevice.state_logic(self, self.States.CHOOSE_AN_ITEM, InputType.INT)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.CHOOSE_AN_ITEM)
        def content() -> dict:
            return ComponentFactory.get(
                ["Select an item to use: "]
                [self._entity.inventory.to_options(lambda item: isinstance(item, items.Usable))]
            )

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
