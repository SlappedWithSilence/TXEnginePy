from enum import Enum

from game.cache import cached
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.messages import ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems.event import Event


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

    def __init__(self):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)

        self._setup_states()

    def _setup_states(self) -> None:
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "PlayerCombatChoiceEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        raise RuntimeError("Loading of PlayerCombatChoiceEvent from JSON is not supported!")

