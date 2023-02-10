import dataclasses
from abc import ABC

from ..currency.currency import CoinPurse
from ..inventory.inventory import Inventory


@dataclasses.dataclass
class Entity(ABC):
    """A basic object that stores an entity's instance attributes such as name, ID, inventory, currencies, etc"""
    name: str
    id: int
    inventory: Inventory = Inventory()
    coin_purse: CoinPurse = CoinPurse()
