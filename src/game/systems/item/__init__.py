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

    def get_value(self, item_id: int, currency: int | Currency) -> Currency:
        """
        Get the value of an item within a specific currency.

        Args:
            item_id: The ID of the item whose value to retrieve
            currency: The ID or an Instance of the currency in which to evaluate the Item's value

        Returns: An instance of currency that contains the value of the item with
        id=item_id in the currency whose id=currency
        """

        currency_id: int = None
        if type(currency) == int:
            currency_id = currency
        elif type(currency) == Currency:
            currency_id = currency.id

        return self._master_item_manifest[item_id].value[currency_id]

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass


item_manager = ItemManager()