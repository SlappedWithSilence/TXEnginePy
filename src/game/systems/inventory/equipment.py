import copy

from game.structures.manager import Manager


class EquipmentManager(Manager):
    """
    The EquipmentManager's duties are to load and distribute data about different equipment slots.
    A game developer may want to add or remove equipment slots to their game and can do so through the equipment manager.
    """

    def __init__(self):
        super().__init__()
        self._slots: dict[str, dict[bool | int]] = {}

    def get_slots(self) -> dict:
        return copy.deepcopy(self._slots)

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass


class EquipmentController:

    def __init__(self):
        self.slots: dict[str, dict[str, bool | int]] = {}