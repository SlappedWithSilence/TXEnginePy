import dataclasses

import game.systems.currency as currency
import game.systems.combat.effect as effect
import game.systems.requirement.requirements as req
from game.structures.loadable import LoadableMixin

from loguru import logger


class Item(LoadableMixin):
    """
    A basic item. Objects of this type are inert.
    """

    def __init__(self, name: str, iid: int, value: dict[int, int], description: str, max_quantity: int = 10):
        super().__init__()
        self.name: str = name  # Name of item
        self.id: int = iid  # Unique id of item
        self.value: dict[int, int] = value  # Item's currency values. Key is Currency.id, value is Currency.quantity
        self.description: str = description  # The user-facing description of the item
        self.max_quantity: int = max_quantity  # The maximum number of items allowed in an inventory stack

    def get_currency_value(self, currency_id: int = None) -> currency.Currency:
        return currency.currency_manager.to_currency(currency_id,
                                                     self.value[currency_id]) if currency is not None else self.value

    @classmethod
    def from_json(cls, json: dict[str, any]):
        """
        Instantiate an Item object from a JSON blob.

        Args:
            json: a dict-form representation of a JSON object

        Returns: An Item instance with the properties defined in the JSON

        Required JSON fields:
        - name: str
        - id: int
        - value: {int, int}
        - description: str

        Optional JSON fields:
        - max_quantity: int (default value 10)
        """


@dataclasses.dataclass
class Usable(Item, req.RequirementsMixin):
    """
    A consumable item. When consumed, this item's stack quantity decreases by 1 and the effects in 'effects' are
    triggered in sequence.
    """
    effects: list[effect.Effect] = dataclasses.field(
        default_factory=list)  # List of effects that trigger when item is used
    consumable: bool = False  # A flag that determines if the item should decrement quantity after each use.

    def use(self, target) -> None:

        from game.systems.entity.entities import Entity
        if not isinstance(target, Entity):
            raise TypeError("Usable target must be an instance of Entity!")

        for e in self.effects:
            e.perform(target)
