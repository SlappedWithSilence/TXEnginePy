from game.structures.manager import Manager
from game.systems.currency.currency import Currency
from game.systems.currency import currency_manager
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

    def get_value(self, item_id: int, curreny: int | Currency) -> str:

        currency_id: int = None
        if type(curreny) == int:
            currency_id = curreny
        elif type(curreny) == Currency:
            currency_id = curreny.id

        return self._master_item_manifest[item_id].value[currency_id]

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass