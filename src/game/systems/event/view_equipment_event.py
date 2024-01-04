from enum import Enum

from game.structures.enums import InputType
from game.structures.messages import ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems.event import Event
from game.systems.event.events import EntityTargetMixin


class ViewEquipmentEvent(EntityTargetMixin, Event):
    class States(Enum):
        DEFAULT = 0
        DISPLAY_EQUIPMENT = 1
        INSPECT_EQUIPMENT = 2
        EMPTY = 3
        TERMINATE = -1

    def __init__(self, **kwargs):
        super().__init__(default_input_type=InputType.SILENT,
                         states=self.States,
                         default_state=self.States.DEFAULT,
                         **kwargs)

        from game.systems.entity.entities import CombatEntity
        if not isinstance(self.target, CombatEntity):
            raise TypeError(f"ViewEquipmentEvent.target must be of type CombatEntity! Got {type(self.target)} instead.")

        self._setup_states()

    def _setup_states(self):
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            self.set_state(self.States.DISPLAY_EQUIPMENT)

        @FiniteStateDevice.state_logic(self, self.States.DISPLAY_EQUIPMENT, InputType.INT)
        def logic(user_input: int) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.DISPLAY_EQUIPMENT)
        def content() -> dict:
            return ComponentFactory.get()

    @staticmethod
    def from_json(json: dict[str, any]) -> any:
        raise NotImplemented("ViewEquipmentEvent does not support JSON loading!")
