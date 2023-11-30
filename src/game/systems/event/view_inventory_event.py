from game.systems.event.events import EntityTargetMixin, Event


class ViewInventoryEvent(EntityTargetMixin, Event):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def from_json(json: dict[str, any]) -> any:
        pass
