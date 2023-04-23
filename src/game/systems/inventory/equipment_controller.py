import game
from game.systems.event.add_item_event import AddItemEvent
from game.systems.inventory import equipment_manager
from game.systems.inventory.equipment_manager import SlotProperties
import game.systems.item as item


class EquipmentController:
    """
    An EquipmentController's duties are to manage the items that an entities.Entity equips. This includes handling the equipping
    and unequipping processes, validating that an item is allowed to fit into a slot.
    """

    @property
    def owner(self) -> any:
        return self._owner

    @owner.setter
    def owner(self, entity) -> None:
        from game.systems.entity import Entity, Player
        if entity is not None and not isinstance(entity, Entity):
            raise TypeError(f"Cannot assign an owner of type {type(entity)}, owner must of type entities.Entity")

        elif entity is None:
            self._owner = None

        elif isinstance(entity, Player):
            self._owner = entity
            self.player_mode = True

        else:
            self._owner = entity
            self.player_mode = False

    def __init__(self, owner=None):
        self.owner = owner
        self.player_mode: bool = False
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

        # If value is a bool, treat is an enable/disable slot
        if type(value) == bool:
            self._slots[key].enabled = value

        # If an int, treat it as set-id
        elif type(value) == int:
            from game.systems.item import item_manager

            ref = item_manager.get_ref(value)
            if not isinstance(ref, item.Equipment):
                raise ValueError(f"Cannot assign item {str(ref)} to slot {key}! Item {str(ref)} is not an Equipment!")

            if ref.slot != key:
                raise ValueError(f"Cannot assign item {str(ref)} to slot {key}! Wrong slot! {key} != {ref.slot}")

            self._slots[key].item_id = value

        # If None, treat it as clear-slot
        elif value is None:
            self._slots[key].item_id = value

        # That's not right
        else:
            raise TypeError(f"Unknown type for value! Expected int, bool, or None. Got {type(value)}!")

    def equip(self, item_id: int) -> bool:
        """
        Pops the item currently in the slot for the item and returns it's ID, then sets slot's id to item_id

        args:
            item_id: The ID of the item to equip

        returns: True if the slot is enabled, false otherwise
        """
        from game.systems.item import item_manager, Equipment

        item_ref = item_manager.get_ref(item_id)

        if isinstance(item_ref, Equipment):
            if not self._slots[item_ref.slot].enabled:
                return False

            self.unequip(item_ref.slot)
            self[item_ref.slot] = item_id
            return True

        raise TypeError(f"Cannot equip item of type {type(item_ref)}! Expected item of type Equipment")

    def unequip(self, slot: str) -> bool:
        """
        Remove the item from a slot and return its ID

        args:
            slot: The name of the slot to empty

        returns: True if the slot is enabled, false otherwise
        """

        if not equipment_manager.is_valid_slot(slot):
            raise ValueError(f"Unknown slot: {slot}!")

        if not self._slots[slot].enabled:
            return False

        temp = self[slot].item_id

        # Spawn an add-item-event to handle placing the removed-item back into player inventory
        if self.player_mode and temp is not None:
            game.state_device_controller.add_state_device(AddItemEvent(temp, 1))
        elif not self.player_mode and temp is not None:
            self.owner.inventory.new_stack(temp, 1)

        self[slot] = None
        return True
