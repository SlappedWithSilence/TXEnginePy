import copy
import weakref

from game.structures.loadable_factory import LoadableFactory
from game.structures.manager import Manager
from game.systems import currency as currency
from game.systems.item import Item
from game.util.asset_utils import get_asset


class ItemManager(Manager):

    ITEM_ASSET_PATH = "items"

    def __init__(self):
        super().__init__()
        self._manifest: dict[int, Item] = {}

    def register_item(self, item_object: Item):
        self._manifest[item_object.id] = item_object

    def get_name(self, item_id: int) -> str:
        return self._manifest[item_id].name

    def get_desc(self, item_id: int) -> str:
        return self._manifest[item_id].description

    def get_costs(self, item_id: int) -> dict[int, int]:
        """
        Get the value of an item in all currencies

        Args:
            item_id: The ID of the item whose value to retrieve

        Returns: A dict that maps an items value in a specific currency to that currency's id
        """

        return self._manifest[item_id].value

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
            return self._manifest[item_id].value[currency_id]
        else:
            return self._manifest[item_id].get_currency_value(currency_id)

    def get_instance(self, item_id: int) -> Item:
        """
        Create and return a deep-copied instance of the item with item.id == 'item_id'

        Args:
            item_id: The ID of the item whose instance to create

        Returns: A deep copy of the requested item
        """
        if type(item_id) != int:
            raise TypeError(f"Item IDs must be of type int! Got {type(item_id)} instead.")

        if item_id not in self._manifest:
            raise ValueError(f"No such item with ID {item_id}!")

        return copy.deepcopy(self._manifest[item_id])

    def get_ref(self, item_id: int) -> Item:
        if type(item_id) != int:
            raise TypeError(f"Item IDs must be of type int! Got {type(item_id)} instead.")

        if item_id not in self._manifest:
            raise ValueError(f"No such item with ID {item_id}!")

        return weakref.proxy(self._manifest[item_id])

    def load(self) -> None:
        raw_asset: dict[str, any] = get_asset(self.ITEM_ASSET_PATH)
        for raw_item in raw_asset['content']:
            item = LoadableFactory.get(raw_item)
            if not isinstance(item, Item):
                raise TypeError(f"Expected object of type Ability, got {type(item)} instead!")

            self.register_item(item)

    def save(self) -> None:
        pass
