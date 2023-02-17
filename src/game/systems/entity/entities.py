import dataclasses
from abc import ABC

import game.systems.currency.currency as currency
import game.systems.inventory.inventory as inv


@dataclasses.dataclass
class Entity(ABC):
    """A basic object that stores an entity's instance attributes such as name, ID, inventory, currencies, etc"""
    name: str
    id: int
    inventory: inv.Inventory = dataclasses.field(default_factory=inv.Inventory)
    coin_purse: currency.CoinPurse = dataclasses.field(default_factory=currency.CoinPurse)
