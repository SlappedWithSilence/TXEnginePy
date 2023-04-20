import copy
from dataclasses import dataclass

from game.structures.manager import Manager
from loguru import logger


@dataclass
class SlotProperties:
    """
    A simple dataclass for storing the properties of an equipment slot.
    """
    name: str  # Name of the slot
    item_id: int | None  # ID of the item placed in the slot
    enabled: bool  # If the slot is allowed to be used

    def unlock(self) -> None:
        """
        Enables the slot.
        """
        if self.enabled:
            logger.warning(f"Slot {self.name} was already enabled!")
        self.enabled = True


class EquipmentManager(Manager):
    """
    The EquipmentManager's duties are to load and distribute data about different equipment slots.
    A game developer may want to add or remove equipment slots to their game and can do so through the equipment manager.
    """

    def __init__(self):
        super().__init__()
        self._slots: dict[str, SlotProperties] = {}

    def __contains__(self, item: str) -> bool:
        return self._slots.__contains__(item)

    def __getitem__(self, item: str) -> SlotProperties:
        return self._slots.__getitem__(item)

    def __setitem__(self, key: str, value: bool | int | None) -> None:
        """
        A wrapper for EquipmentManager::_slots::__set_item__.

        If the value passed is of type bool, it is assumed that this value is intended for the SlotProperties::enabled
        field. If the value is of type int or None, it is assumed that this value is intended for the
        SlotProperties::item_id field.
        """

        if key not in self._slots:
            raise KeyError(f"Unknown slot: {key}!")

        if type(value) == bool:
            self._slots[key].enabled = value

        elif type(value) == int or value is None:
            self._slots[key].item_id = value

        else:
            raise TypeError(f"Unknown type for value! Expected int, bool, or None. Got {type(value)}!")

    def register_slot(self, name: str, enabled=True) -> None:
        """
        Registers a new slot with the EquipmentManager.
        """
        if name in self._slots:
            raise ValueError(f"Cannot register slot with name {name}, slot already exists!")

        if type(name) != str or len(name) < 1:
            raise TypeError("Invalid name! Equipment slot names must be strings of length > 1!")

        if type(enabled) != bool:
            raise TypeError(f"Enabled must be of type bool! Got {type(enabled)} instead.")

        self._slots[name] = SlotProperties(name, None, enabled)

    def get_slots(self) -> dict:
        return copy.deepcopy(self._slots)

    def is_valid_slot(self, slot: str) -> str:
        """
        Validates that a given slot key exists. If it does, return the slot. Otherwise, raise an Error.

        args:
            slot: The slot key to validate

        returns: slot if slot exists, None otherwise
        """
        if slot in self._slots:
            return slot

        raise ValueError(f"Slot {slot} does not exist! Possible slots are {','.join(list(self._slots.keys()))}")

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass
