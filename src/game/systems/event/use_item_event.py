from enum import Enum

from game.cache import cached, from_cache
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice
from game.systems.event.events import Event


class UseItemEvent(Event):
    class States(Enum):
        DEFAULT = 0
        USE_ITEM = 1
        NOT_USABLE = 2
        NOT_REQUIREMENTS = 3
        TERMINATE = -1

    def __init__(self, stack_index: int, target = None):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self.stack_index = stack_index
        self._target = target  # Type Entity

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

            from game.systems.item.item import Usable
            if isinstance(self.target.inventory.items[self.stack_index].ref, Usable):

                if self.target.inventory.items[self.stack_index].ref.is_requirements_fulfilled(self.target):
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
            ref = self.target.inventory.items[self.stack_index].ref
            c = [
                "Failed to use ",
                StringContent(value=ref.name, formatting="item_name"),
                ". Requirements are not met."
            ]
            return ComponentFactory.get(c, ref.get_requirements_as_options())

        @FiniteStateDevice.state_logic(self, self.States.NOT_USABLE, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.NOT_USABLE)
        def content() -> dict:
            return ComponentFactory.get(
                [
                    StringContent(value=self.target.inventory.items[self.stack_index].ref.name,
                                  formatting="item_name"),
                    " cannot be used."
                ]
            )

        @FiniteStateDevice.state_logic(self, self.States.USE_ITEM, InputType.ANY)
        def logic(_: any) -> None:
            stack = self.target.inventory.items[self.stack_index]
            stack.ref.use(self.target)

            if stack.ref.consumable:
                stack.quantity = stack.quantity - 1

            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.USE_ITEM)
        def content() -> dict:
            stack = self.target.inventory.items[self.stack_index]

            return ComponentFactory.get(
                [
                    "You used ",
                    stack.ref.name,
                    "."
                ]
            )

    @property
    def target(self):
        return self._target or from_cache('player')

    def __copy__(self):
        return UseItemEvent(self.stack_index)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "UseItemEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        raise RuntimeError("UseItemEvent does not support JSON loading!")
