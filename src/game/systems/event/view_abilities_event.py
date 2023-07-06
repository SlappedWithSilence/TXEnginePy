from enum import Enum

from game.cache import cached, from_cache
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.messages import ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems.entity.entities import AbilityMixin
from game.systems.event import Event


class ViewAbilitiesEvent(Event):
    class States(Enum):
        DEFAULT = 0
        VIEW_ABILITIES = 1
        INSPECT_ABILITY = 2
        TERMINATE = -1

    def __init__(self, target: AbilityMixin = None):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self.target: AbilityMixin = target  # Defaults to the player at runtime
        self.selected_ability: str | None = None

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

            if self.target is None:
                self.target = from_cache('player')

            if not isinstance(self.target, AbilityMixin):
                raise TypeError(f"Cannot view Abilities for non-AbilityMixin entity! ({self.target})")

            self.set_state(self.States.VIEW_ABILITIES)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        # This state is highly inefficient. TODO: Improve
        @FiniteStateDevice.state_logic(self, self.States.VIEW_ABILITIES, InputType.INT,
                                       -1, lambda: len(list(self.target.ability_controller.abilities)) - 1)
        def logic(user_input: int) -> None:
            if user_input == -1:
                self.set_state(self.States.TERMINATE)

            self.selected_ability = list(self.target.ability_controller.abilities)[user_input]

        @FiniteStateDevice.state_content(self, self.States.VIEW_ABILITIES)
        def content() -> dict:
            pass

        @FiniteStateDevice.state_logic(self, self.States.INSPECT_ABILITY, InputType.ANY)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.INSPECT_ABILITY)
        def content() -> dict:
            pass

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ViewAbilitiesEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        return ViewAbilitiesEvent()
