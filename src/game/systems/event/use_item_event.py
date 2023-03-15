from enum import Enum

import game
from game import cache
from game.structures.enums import InputType
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice
from game.systems.entity import entities as entities
from game.systems.event.events import Event
from game.systems.item.item import Usable


class UseItemEvent(Event):
    class States(Enum):
        DEFAULT = 0
        USE_ITEM = 1
        NOT_USABLE = 2
        NOT_REQUIREMENTS = 3
        TERMINATE = -1

    def __init__(self, stack_index: int):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
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

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.NOT_REQUIREMENTS, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.NOT_REQUIREMENTS)
        def content(_: any) -> dict:
            c = [
                "Failed to use ",
                StringContent(value=self.player_ref.inventory.items[self.stack_index].ref.name, formatting="item_name"),
                ". Requirements are not met."
            ]
            return ComponentFactory.get(c)

        @FiniteStateDevice.state_logic(self, self.States.NOT_USABLE, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.NOT_USABLE)
        def content() -> dict:
            return ComponentFactory.get(
                [
                    StringContent(value=self.player_ref.inventory.items[self.stack_index].ref.name,
                                  formatting="item_name"),
                    " cannot be used."
                ]
            )

        @FiniteStateDevice.state_logic(self, self.States.USE_ITEM, InputType.ANY)
        def logic(_: any) -> None:
            stack = self.player_ref.inventory.items[self.stack_index]
            stack.ref.use()

            if stack.ref.consumable:
                stack.quantity = stack.quantity - 1

            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.USE_ITEM)
        def content() -> dict:
            stack = self.player_ref.inventory.items[self.stack_index]

            return ComponentFactory.get(
                [
                    "You used ",
                    stack.ref.name,
                    "."
                ]
            )

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.set_dead()

        @FiniteStateDevice.state_content(self, self.States.TERMINATE)
        def content() -> dict:
            return ComponentFactory.get()
