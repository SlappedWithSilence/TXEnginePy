from enum import Enum
from typing import Callable

from game.cache import cached, request_store, store_element
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.messages import ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems.event import Event
from game.systems.event.events import EntityTargetMixin


class SelectItemEvent(EntityTargetMixin, Event):
    """
    Select an item from an entity's inventory and return the selected item's ID
    """

    class States(Enum):
        DEFAULT = 0
        SHOW_ITEMS = 1
        STORE_CHOICE = 2
        TERMINATE = 3

    def __init__(self, target, inventory_filter: Callable = None):
        super().__init__(target=target,
                         default_input_type=InputType.SILENT, states=self.States, default_state=self.States.DEFAULT)
        self._storage_keys: dict[str, str | None] = {'selected_item_id': None}
        self._inventory_filter = inventory_filter

    def _link(self) -> dict[str, str]:
        """
        Override default link logic to reserve a key for the item_id that was selected by the user
        """
        self._storage_keys["selected_item_id"] = request_store()
        return self._storage_keys

    def _setup_states(self) -> None:
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            self.set_state(self.States.SHOW_ITEMS)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.SHOW_ITEMS, InputType.INT, -1,
                                       len(self.target.inventory.filter_stacks(self._inventory_filter)) - 1)
        def logic(user_input: int):
            if self._storage_keys['selected_item_id'] is None:
                raise RuntimeError("SelectItemEvent was never linked!")

            # Store the user's item choice in the storage via the key generated from `_link()`
            store_element(self._storage_keys['selected_item_id'],
                          self.target.inventory.filter_stacks(self._inventory_filter)[user_input].id)

        @FiniteStateDevice.state_content(self, self.States.SHOW_ITEMS)
        def content():
            return ComponentFactory.get(
                ["Choose an item:"],
                self.target.inventory.to_options(self._inventory_filter)
            )

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "SelectItemEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        return SelectItemEvent(None)
