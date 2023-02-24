from game.structures.manager import Manager
from game.systems.currency.currency import Currency
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

    def get_cost(self, item_id: int, currency_id: int) -> int:
        """
        Get the value of an item in a specific currency

        Args:
            item_id: The ID of the item to look up
            currency_id: The ID of the currency to look up

        Returns: An int value representing the item's cost in currency 'currency_id'
        """
        return self._master_item_manifest[item_id].value[currency_id]

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass


item_manager = ItemManager()
