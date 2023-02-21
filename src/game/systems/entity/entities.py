from dataclasses import dataclass, field
from abc import ABC

import game.systems.currency.currency as currency
import game.systems.inventory.inventory as inv
import game.systems.entity.resource as resource


@dataclass
class Entity(ABC):
    """A basic object that stores an entity's instance attributes such as name, ID, inventory, currencies, etc"""
    name: str
    id: int
    inventory: inv.Inventory = field(default_factory=inv.Inventory)
    coin_purse: currency.CoinPurse = field(default_factory=currency.CoinPurse)
    resources: resource.ResourceController = field(default_factory=resource.ResourceController)


class Player(Entity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
