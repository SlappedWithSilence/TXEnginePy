from game.cache import cached
from game.structures.loadable import LoadableMixin
from game.systems.event.events import EntityTargetMixin, Event


class ViewInventoryEvent(EntityTargetMixin, Event):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ViewSkillsEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        raise NotImplementedError("ViewInventoryEvent does not support JSON loading!")
