from abc import ABC

import game.systems.currency.coin_purse
import game.systems.entity.resource as resource
import game.systems.inventory.inventory_controller as inv
from game.cache import cached
from game.structures.loadable import LoadableMixin, LoadableFactory
from game.systems.inventory import EquipmentController

from loguru import logger


class InventoryMixin:
    """
    A mixin for Entity objects that provides Inventory functionality.
    """

    def __init__(self, inventory: inv.InventoryController = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        An InventoryController's content may be provided via instance, by tuple, or both.
        """
        if inventory is None:
            logger.debug("Using default inventory")
        else:
            logger.debug("Valid inventory found!")
            logger.debug(str(inventory.items))
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

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Entity", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
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
        kw = {}
        for attr in json['attributes']:
            kw[attr] = LoadableFactory.get(json['attributes'][attr][0])

        e = Entity(json['name'], json['id'], **kw)

        # Post-init fixing
        # Note: since the equipment_controller only gets assigned an owner assigned AFTER init, it cannot check equip
        #       requirements. Thus, when loading the player's equipment_controller, can allow equipment to be equipped
        #       that the player cannot normally equip.
        if "equipment_controller" in kw:
            e.equipment_controller.owner = e

        return e


class AbilityMixin:
    """
    A Mixin that grants an Entity the capacity to learn Abilities
    """

    def __init__(self, abilities: list[str] = None, ability_controller = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ability_controller = ability_controller or "REPLACE WITH ACTUAL ABILITY CONTROLLER"
        if abilities is not None:
            for ability in abilities:
                self.ability_controller.learn(ability)


class CombatEntity(AbilityMixin, Entity):

    def __init__(self, name: str, entity_id: int,
                 xp_yield: int = 1,
                 abilities: list[str] = None,
                 ability_controller=None,
                 turn_speed: int = 1,
                 *args, **kwargs):
        super().__init__(name, entity_id, abilities=abilities, ability_controller=ability_controller, *args, **kwargs)
        self.xp_yield: int = xp_yield
        self.turn_speed = turn_speed


class Player(Entity):

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Player", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__("Player", *args, **kwargs)
