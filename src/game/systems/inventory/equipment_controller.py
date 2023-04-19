from game.systems.inventory import equipment_manager
from game.systems.inventory.equipment_manager import SlotProperties


class EquipmentController:
    """
    An EquipmentController's duties are to manage the items that an Entity equips. This includes handling the equipping
    and unequipping processes, validating that an item is allowed to fit into a slot.
    """

    def __init__(self):
        self._slots: dict[str, SlotProperties] = equipment_manager.get_slots()

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