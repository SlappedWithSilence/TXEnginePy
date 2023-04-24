from abc import ABC

import game.systems.currency.coin_purse
import game.systems.entity.resource as resource
import game.systems.inventory.inventory_controller as inv
from game.cache import cached, get_loader
from game.structures.loadable import LoadableMixin
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


class Entity(LoadableMixin, ABC):
    """A basic object that stores an entity's instance attributes such as name, ID, inventory, currencies, etc"""

    def __init__(self, name: str, entity_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.id: int = entity_id

    @cached(LoadableMixin.LOADER_KEY, "Entity")
    def from_json(self, json: dict[str, any]) -> any:
        return EntityFactory.get(json)


class Player(ResourceMixin, CurrencyMixin, InventoryMixin, Entity):

    @cached(LoadableMixin.LOADER_KEY, "Player")
    def from_json(self, json: dict[str, any]) -> any:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(name="Player", entity_id=0, *args, **kwargs)


class EntityFactory:
    cls_map = {cls.__name__.__str__(): cls for cls in [InventoryMixin, CurrencyMixin, ResourceMixin, EquipmentMixin]}

    @classmethod
    def _get_type(cls, classes: list[str]):

        def constructor(self, *args, **kwargs):
            print(type(self).__mro__)
            type(self).__mro__[1].__init__(self, *args, **kwargs)

        try:
            types: list[type] = [cls.cls_map[c] for c in classes] + [Entity]
        except KeyError:
            raise KeyError(f"One or more classes in {str(classes)} were not found by EntityFactory!")
        return type("MutableEntity", tuple(types), {
            "__init__": constructor
        })

    @classmethod
    def _is_loadable(cls, json: dict) -> bool:
        if type(json) == dict:

            if 'class' in json:
                return True

        return False

    @classmethod
    def get(cls, json: dict[str, any]):
        """
        Generate an Entity object instance with the appropriate attribute definitions from a json file.
        """
        entity_cls: type = cls._get_type(json['features'])
        entity_instance: Entity = entity_cls(name=json['name'], entity_id=json['id'])

        # For each attribute
        for attr in json['attributes']:
            if hasattr(entity_instance, attr) and cls._is_loadable(json['attributes'][attr]):
                entity_instance.__setattr__(
                    attr, get_loader(
                        json['attributes'][attr]['class']
                    )(json['attributes'][attr])
                )
            elif hasattr(entity_instance, attr):
                entity_instance.__setattr__(attr, json['attributes'][attr])

        return entity_instance


