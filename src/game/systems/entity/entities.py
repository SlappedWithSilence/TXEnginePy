from abc import ABC

import game.systems.currency.coin_purse
import game.systems.entity.resource as resource
import game.systems.inventory.inventory_controller as inv
from game.cache import cached
from game.structures.loadable import LoadableMixin, LoadableFactory
from game.systems.inventory import EquipmentController


class InventoryMixin:
    """
    A mixin for Entity objects that provides Inventory functionality.
    """

    def __init__(self, inventory: inv.InventoryController = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        An InventoryController's content may be provided via instance, by tuple, or both.
        """
        self.inventory = inventory or inv.InventoryController()


class CurrencyMixin:
    """
    A mixin for Entity objects that provides CoinPurse functionality.
    """

    def __init__(self, coin_purse=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coin_purse = coin_purse or game.systems.currency.coin_purse.CoinPurse()


class ResourceMixin:
    """
    A mixin for Entity objects that provides ResourceController functionality
    """

    def __init__(self, resource_controller: resource.ResourceController = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_controller: resource.ResourceController = resource_controller or resource.ResourceController()


class EquipmentMixin:
    """
    A mixin for Entity objects that provides EquipmentController functionality
    """

    def __init__(self, equipment_controller: EquipmentController = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equipment_controller = equipment_controller or EquipmentController()
        self.equipment_controller.owner = self


class Entity(EquipmentMixin, ResourceMixin, CurrencyMixin, InventoryMixin, LoadableMixin):
    """A basic object that stores an entity's instance attributes such as name, ID, inventory, currencies, etc"""

    def __init__(self, name: str, entity_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.id: int = entity_id

    @cached(LoadableMixin.LOADER_KEY, "Entity")
    def from_json(self, json: dict[str, any]) -> any:
        """
        Instantiate an Entity object from a JSON blob.

        Args:
            json: a dict-form representation of a json object

        Returns: an Entity instance with the properties defined in the JSON

        Required JSON fields:
        - name: str
        - id: int
        - attributes: [any]

        Optional attribute fields:
        - inventory_controller: InventoryController
        - resource_controller: ResourceController
        - equipment_controller: EquipmentController
        - coin_purse: CoinPurse

        Optional JSON fields:
        - None
        """

        # Turn the attributes JSON fields into key-word arguments to be passed to Entity's subclasses
        kwargs = {}
        for attr in json['attributes']:
            kwargs[attr]['class'] = LoadableFactory.get(attr)

        e = Entity(json['name'], json['id'], kwargs=kwargs)

        # Post-init fixing
        # Note: since the equipment_controller only gets assigned an owner assigned AFTER init, it cannot check equip
        #       requirements. Thus, when loading the player's equipment_controller, can allow equipment to be equipped
        #       that the player cannot normally equip.
        if "equipment_controller" in kwargs:
            e.equipment_controller.owner = e

        return e


class Player(Entity):

    @cached(LoadableMixin.LOADER_KEY, "Player")
    def from_json(self, json: dict[str, any]) -> any:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__("Player", *args, **kwargs)
