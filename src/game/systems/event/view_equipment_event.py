from __future__ import annotations

from enum import Enum

import rich.pretty

from game.cache import from_cache
from game.structures import enums
from game.structures.enums import InputType
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice
from game.systems.event import Event
from game.systems.event.events import EntityTargetMixin
from game.systems.item.item import Equipment

from game.systems.entity.entities import CombatEntity


class ViewEquipmentEvent(EntityTargetMixin, Event):
    class States(Enum):
        DEFAULT = 0
        DISPLAY_EQUIPMENT = 1
        INSPECT_EQUIPMENT = 2
        SLOT_IS_EMPTY = 3
        TERMINATE = -1

    def __init__(self, target: CombatEntity, **kwargs):
        super().__init__(default_input_type=InputType.SILENT,
                         states=self.States,
                         default_state=self.States.DEFAULT,
                         target=target,
                         **kwargs)

        self._inspect_item_id: int = None

        if not isinstance(self.target, CombatEntity):
            raise TypeError(f"ViewEquipmentEvent.target must be of type CombatEntity! Got {type(self.target)} instead.")

        self._setup_states()

    def _setup_states(self):
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            self.set_state(self.States.DISPLAY_EQUIPMENT)

        @FiniteStateDevice.state_logic(self, self.States.DISPLAY_EQUIPMENT, InputType.INT, input_min=-1,
                                       input_max=lambda: len(self.target.equipment_controller.enabled_slots) - 1)
        def logic(user_input: int) -> None:
            if user_input == -1:
                self.set_state(self.States.TERMINATE)
                return

            slot = self.target.equipment_controller.enabled_slots[user_input]
            if self.target.equipment_controller[slot].item_id is None:
                self.set_state(self.States.SLOT_IS_EMPTY)
                return

            self._inspect_item_id = self.target.equipment_controller[slot].item_id
            self.set_state(self.States.INSPECT_EQUIPMENT)

        @FiniteStateDevice.state_content(self, self.States.DISPLAY_EQUIPMENT)
        def content() -> dict:
            return ComponentFactory.get(
                [self.target.name, "'s Equipment:"],
                self.target.equipment_controller.get_equipment_as_options()
            )

        @FiniteStateDevice.state_logic(self, self.States.SLOT_IS_EMPTY, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.DISPLAY_EQUIPMENT)

        @FiniteStateDevice.state_content(self, self.States.SLOT_IS_EMPTY)
        def content() -> dict:
            return ComponentFactory.get(
                ["This equipment slot is empty."]
            )

        @FiniteStateDevice.state_logic(self, self.States.INSPECT_EQUIPMENT, InputType.ANY)
        def logic(_: any) -> None:
            return self.set_state(self.States.DISPLAY_EQUIPMENT)

        @FiniteStateDevice.state_content(self, self.States.INSPECT_EQUIPMENT)
        def content() -> dict:
            ref: Equipment = from_cache("managers.ItemManager").get_instance(self._inspect_item_id)
            rich.pretty.pprint(ref.__dict__)
            return ComponentFactory.get(
                [
                    ref.name, "'s Summary",
                    "\n",
                    ref.functional_description,
                    "\n",
                    ref.description,
                    "\n",
                    "damage: ", StringContent(value=str(ref.damage_buff), style="combat_damage"),
                    "\n"
                    "armor: ", StringContent(value=str(ref.damage_resist), style="combat_resist")
                ]
            )

    @staticmethod
    def from_json(json: dict[str, any]) -> any:
        raise NotImplemented("ViewEquipmentEvent does not support JSON loading!")
