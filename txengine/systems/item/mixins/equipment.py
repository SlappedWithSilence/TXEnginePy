from txengine.types.enums import EquipmentType


class EquipmentMixin:
    """Gives an item the characteristics of an equipment."""

    def __init__(self):
        self.equipment_type: EquipmentType = None
        self.pre_combat_effects: list = []  # A list of effects that are executed at the start of combat
        self.tag_resistances: list[(str, float)] = []  # Resistance given to the user for effects with a given tag
        self.equip_requirements: list = []  # Requirements the user must meet to be able to equip item
        self.ability_names: list[str] = []  # Names of the abilities the item gives to the user when equipped
        self.damage_bonus: int = 0  # Flat damage bonus given to the user's abilities
        self.damage_resistance: int = 0  # % damage resistance given to the user