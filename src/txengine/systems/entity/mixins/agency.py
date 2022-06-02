from ...item.mixins.equipment import EquipmentMixin
from ....structures.enums import EquipmentType
from ...item.item_util import reference, item_name
from ....ui.color import style

from rich import print


class AgencyMixin:
    """ An entity that inherits from AgencyMixin is capable of taking part in combat and making turn choices
        An entity that inherits from AgencyMixin is also capable of wearing equipment.
    """

    def __init__(self, equipment: dict[EquipmentType, int], abilities: set[str], mode: int = 0):
        self.equipment: dict[EquipmentType, int] = equipment
        self.mode: int = mode
        self.abilities: set[str] = abilities

    def take_turn(self, combat_context: any) -> any:
        """The entity calculates the next combat action to take and returns it"""
        raise NotImplementedError(f"Entity {self} does not implement take_turn! This is a required function.")

    def equip_item(self, item_id) -> [int, None]:
        """ Attempts to auto-equip a given item to the entity.

            If an item already exists in that slot, it gets auto-unequipped.
        """
        item = reference(item_id)  # Get a reference to the item object for the given id
        if isinstance(item, EquipmentMixin):  # Check if its an Equipment
            unequipped_item = None
            if self.equipment[item.equipment_type]:  # Check if slot is occupied
                unequipped_item = reference(self.equipment[item.equipment_type]).id  # Return the current slot's item id

            self.equipment[item.equipment_type] = item_id

            return unequipped_item

        else:
            print(style(f"Cannot equip {item_name(item_id)}!", "error"))

    def unequip_item(self, slot: EquipmentType) -> int:
        unequipped_item = reference(self.equipment[slot]).id
        self.equipment[slot] = None
        return unequipped_item
