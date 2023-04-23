from abc import ABC

import game.systems.currency.coin_purse
import game.systems.entity.resource as resource
import game.systems.inventory.inventory_controller as inv
from game.systems.inventory import EquipmentController


class InventoryMixin:
    """
    A mixin for Entity objects that provides Inventory functionality.
    """

    def __init__(self, inventory: inv.InventoryController = None, item_manifest: list[tuple[int, int]] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        An InventoryController's content may be provided via instance, by tuple, or both.
        """
        self.inventory = inventory or inv.InventoryController()

        if item_manifest:
            for item_id, item_quantity in item_manifest:
                self.inventory.new_stack(item_id, item_quantity, True)


class CurrencyMixin:
    """
    A mixin for Entity objects that provides CoinPurse functionality.
    """

    def __init__(self, coin_purse=None, currency_manifest: list[tuple[int, int]] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coin_purse = coin_purse or game.systems.currency.coin_purse.CoinPurse()

        if currency_manifest:
            for currency_id, currency_quantity in currency_manifest:
                self.coin_purse.adjust(currency_id, currency_quantity)


class ResourceMixin:
    """
    A mixin for Entity objects that provides ResourceController functionality
    """

    def __init__(self, resource_controller: resource.ResourceController = None,
                 resource_manifest: list[tuple[str, int, int]] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_controller: resource.ResourceController = resource_controller or resource.ResourceController()

        if resource_manifest:
            self.resource_controller = resource.ResourceController(resource_manifest)


class EquipmentMixin:
    """
    A mixin for Entity objects that provides EquipmentController functionality
    """

    def __init__(self, equipment_controller: EquipmentController = None,
                 equipment_manifest: list[int] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equipment_controller = equipment_controller or EquipmentController()
        self.equipment_controller.owner = self

        # Override the currently-equipped items. The items that are overriden are lost forever.
        if equipment_manifest:
            for equipment_id in equipment_manifest:
                equipment_controller.equip(equipment_id)


class Entity(ABC):
    """A basic object that stores an entity's instance attributes such as name, ID, inventory, currencies, etc"""

    def __init__(self, name: str, entity_id: int):
        self.name: str = name
        self.id: int = entity_id


class Player(ResourceMixin, CurrencyMixin, InventoryMixin, Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(name="Player", entity_id=0, *args, **kwargs)
