import copy

import game.structures.manager as manager
from .currency import Currency


class CurrencyManager(manager.Manager):
    """
    An object that manages TXEngine's Currency system. This includes loading and saving currency asset definitions,
    validating various currency conversions, and more.
    """

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass

    def __init__(self):
        super().__init__()
        self.currencies: dict[int, Currency] = {}

    def to_currency(self, currency_id: int, quantity: int) -> Currency:
        """
        Convert a currency id and quantity into a Currency object.

        Args:
            currency_id (int): The ID of the currency to instantiate
            quantity (int):  The quantity to set the currency to
        """

        cur = copy.deepcopy(self.currencies[currency_id])
        cur.quantity = quantity
        return cur


currency_manager = CurrencyManager()
