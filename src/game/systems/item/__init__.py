import copy

import game.systems.currency as currency
from game.structures.manager import Manager
from game.systems.item.item import Item


class ItemManager(Manager):

    def __init__(self):
        super().__init__()
        self._master_item_manifest: dict[int, Item] = {}

    def register_item(self, item_object: Item):
        self._master_item_manifest[item_object.id] = item_object

    def get_name(self, item_id: int) -> str:
        return self._master_item_manifest[item_id].name

    def get_desc(self, item_id: int) -> str:
        return self._master_item_manifest[item_id].description

    def get_costs(self, item_id: int) -> dict[int, int]:
        """
        Get the value of an item in all currencies

        Args:
            item_id: The ID of the item whose value to retrieve

        Returns: A dict that maps an items value in a specific currency to that currency's id
        """

        return self._master_item_manifest[item_id].value

    def get_cost(self, item_id: int, currency_id: int, as_currency: bool = False) -> int | currency.Currency:
        """
        Get the value of an item in a specific currency

        Args:
            item_id: The ID of the item to look up
            currency_id: The ID of the currency to look up
            as_currency: If True, return an instance of a currency instead of an int

        Returns: An int value representing the item's cost in currency 'currency_id'
        """
        if not as_currency:
            return self._master_item_manifest[item_id].value[currency_id]
        else:
            return self._master_item_manifest[item_id].get_currency_value(currency_id)

    def get_instance(self, item_id: int) -> item.Item:
        """
        Create and return a deep-copied instance of the item with item.id == 'item_id'

        Args:
            item_id: The ID of the item whose instance to create

        Returns: A deep copy of the requested item
        """
        if type(item_id) != int:
            raise TypeError(f"Item IDs must be of type int! Got {type(item_id)} instead.")

        if item_id not in self._master_item_manifest:
            raise ValueError(f"No such item with ID {item_id}!")

        return copy.deepcopy(self._master_item_manifest[item_id])

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass


item_manager = ItemManager()
