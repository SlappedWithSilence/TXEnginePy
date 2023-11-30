from game.systems.event import Event
from game.systems.event.events import EntityTargetMixin


class ViewEquipmentEvent(EntityTargetMixin, Event):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._setup_states()

    def _setup_states(self):
        pass


    @staticmethod
    def from_json(json: dict[str, any]) -> any:
        raise NotImplemented("ViewEquipmentEvent does not support JSON loading!")