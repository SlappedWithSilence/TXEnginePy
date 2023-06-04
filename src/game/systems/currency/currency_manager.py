import copy

from game.structures import manager as manager
from game.structures.loadable_factory import LoadableFactory
from game.systems.currency import Currency
from game.util.asset_utils import get_asset


class CurrencyManager(manager.Manager):
    """
    An object that manages TXEngine's Currency system. This includes loading and saving currency asset definitions,
    validating various currency conversions, and more.
    """

    CURRENCY_ASSET_PATH = "currencies"

    def __init__(self):
        super().__init__()
        self._manifest: dict[int, Currency] = {}

    def __contains__(self, item: int | Currency):
        if type(item) == int:
            return item in self._manifest
        elif type(item) == Currency:
            return item.id in self._manifest
        else:
            return False

    def __iter__(self):
        return self._manifest.values().__iter__()

    def to_currency(self, currency_id: int, quantity: int) -> Currency:
        """
        Convert a currency id and quantity into a Currency object.

        Args:
            currency_id (int): The ID of the currency to instantiate
            quantity (int):  The quantity to set the currency to
        """

        cur = copy.deepcopy(self._manifest[currency_id])
        cur.quantity = quantity
        return cur

    def register_currency(self, currency: Currency):
        if currency.id in self._manifest:
            raise ValueError(f"Currency with id {currency.id} already exists!")

        self._manifest[currency.id] = currency

    def load(self) -> None:
        raw_asset = get_asset(self.CURRENCY_ASSET_PATH)

        for raw_currency in raw_asset['content']:
            currency = LoadableFactory.get(raw_currency)

            if not isinstance(currency, Currency):
                raise TypeError(f"Expected object of type Currency, got type {type(currency)} instead!")

            self.register_currency(currency)

    def save(self) -> None:
        pass
