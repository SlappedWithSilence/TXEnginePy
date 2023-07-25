from game.cache import cached, from_cache
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.systems.event import Event


class SelectItemEvent(Event):
    """
    Select an item from an entity's inventory and return the selected item's ID
    """

    def __init__(self, target):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self._target = target

    @property
    def target(self):
        return self._target or from_cache('player')

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "SelectItemEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        return SelectItemEvent()
