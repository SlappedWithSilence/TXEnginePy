import dataclasses

from ..currency.currency import Currency
from ..requirement.requirements import RequirementsMixin


@dataclasses.dataclass
class Item:
    """
    A basic item. Objects of this type are intert.
    """
    name: str  # Name of item
    id: int  # Unique id of item
    value: dict[tuple[int, str], Currency]  # A map of currency values for the item. The primary key is Currency.key
    max_quantity: int  # The maximum number of items allowed in an inventory stack
    description: str  # The user-facing description of the item


@dataclasses.dataclass
class Consumable(Item, RequirementsMixin):
    """
    A consumable item. When consumed, this item's stack quantity decreases by 1 and the effects in 'effects' are
    triggered in sequence.
    """
    effects: list = dataclasses.field(default_factory=list)  # A list of effects that trigger when the item is consumed
