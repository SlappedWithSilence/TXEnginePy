import dataclasses

import game.systems.currency as currency
import game.systems.combat.effect as effect
import game.systems.requirement.requirements as req


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

    def get_currency_value(self, currency_id: int) -> currency.Currency:
        return currency.currency_manager.to_currency(currency_id, self.value[currency_id])


@dataclasses.dataclass
class Usable(Item, req.RequirementsMixin):
    """
    A consumable item. When consumed, this item's stack quantity decreases by 1 and the effects in 'effects' are
    triggered in sequence.
    """
    effects: list[effect.Effect] = dataclasses.field(default_factory=list)  # List of effects that trigger when item is used
    consumable: bool = False  # A flag that determines if the item should decrement quantity after each use.

    def use(self, target) -> None:

        from game.systems.entity.entities import Entity
        if not isinstance(target, Entity):
            raise TypeError("Usable target must be an instance of Entity!")

        for e in self.effects:
            e.perform(target)

