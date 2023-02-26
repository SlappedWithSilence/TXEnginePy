import dataclasses

from ..combat.effect import Effect
from ..entity.entities import Entity
from ..requirement.requirements import RequirementsMixin


@dataclasses.dataclass
class Item:
    """
    A basic item. Objects of this type are inert.
    """
    name: str  # Name of item
    id: int  # Unique id of item
    value: dict[int, int]  # Item's currency values. The primary key is Currency.id, the value is Currency.quantity
    description: str  # The user-facing description of the item
    max_quantity: int = 10  # The maximum number of items allowed in an inventory stack


@dataclasses.dataclass
class Usable(Item, RequirementsMixin):
    """
    A consumable item. When consumed, this item's stack quantity decreases by 1 and the effects in 'effects' are
    triggered in sequence.
    """
    effects: list[Effect] = dataclasses.field(default_factory=list)  # List of effects that trigger when item is used
    consumable: bool = False  # A flag that determines if the item should decrement quantity after each use.

    def use(self, target: Entity) -> None:
        for effect in self.effects:
            effect.perform(target)

