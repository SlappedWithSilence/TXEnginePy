from ...effect.effect import Effect
from ....structures.enums import EquipmentType


class EquipmentMixin:
    """Gives an item the characteristics of an equipment."""

    def __init__(self, equipment_type: EquipmentType,
                 pre_combat_effects: list[Effect] = None,
                 tag_resistances: dict[str, float] = None,
                 equip_requirements: list[any] = None,
                 abilities: list[str] = None,
                 damage_bonus: int = 0,
                 damage_resistance: float = 0.0):
        
        self.equipment_type: EquipmentType = equipment_type
        self.pre_combat_effects: list = pre_combat_effects or []  # effects that trigger at the start of combat
        self.tag_resistances: dict[str, float] = tag_resistances or {}  # % resistance to a given effect tag
        self.equip_requirements: list = equip_requirements or []  # Requirements that must meet to be able to equip item
        self.abilities: list[str] = abilities or []  # Names of the abilities the item gives to the user when equipped
        self.damage_bonus: int = damage_bonus  # Flat damage bonus given to the user's abilities
        self.damage_resistance: float = damage_resistance  # % damage resistance given to the user
