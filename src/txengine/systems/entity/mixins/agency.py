from ...item.mixins.equipment import EquipmentMixin
from ....structures.enums import EquipmentType
from ...item.item_util import reference, item_name
from ....ui.color import style

from rich import print


class AgencyMixin:
    """ An entity that inherits from AgencyMixin is capable of taking part in combat and making turn choices
        An entity that inherits from AgencyMixin is also capable of wearing equipment.
    """

    def __init__(self, equipment: dict[EquipmentType, int], mode: int = 0):
        self.equipment = equipment
        self.mode = mode

    def take_turn(self, combat_context: any) -> any:
        """The entity calculates the next combat action to take and returns it"""
        raise NotImplementedError(f"Entity {self} does not implement take_turn! This is a required function.")

    def equip_item(self, item_id) -> [int, None]:
        """ Attempts to auto-equip a given item to the entity.

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
