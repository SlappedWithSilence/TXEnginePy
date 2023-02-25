import dataclasses

from game.cache import get_cache
from game.systems.currency import Currency


@dataclasses.dataclass
class CoinPurse:
    currencies: dict[int, Currency] = dataclasses.field(default_factory=dict)

    def balance(self, cur: Currency | int) -> int:
        # If the passed value is a Currency
        if type(cur) == Currency:
            if cur.id in self.currencies:
                return self.currencies[cur.id].quantity

        # TODO: Improve lookup syntax
        # If the passed type is Currency.id or Currency.name
        if type(cur) == int:
            return self.currencies[cur].quantity

        return 0

    def spend(self, cur: Currency | int, quantity: int | None = None) -> bool:
        """
        Attempt to spend currency.

        Args:
            cur: the currency to spend, or the id of the currency to spend
            quantity: The amount of the currency to spend

        Returns: True if the currency was successfully spent, False otherwise
        """
        if type(cur) == Currency:
            if self.balance(cur) >= cur.quantity:
                self.currencies[cur.id] = self.currencies[cur.id] - cur
                return True

        elif (type(cur) == int) and type(quantity) == int:
            if self.balance(cur) >= quantity:
                self.currencies[cur.id] = self.currencies[cur.id] - quantity
                return True

        return False

    def test_currency(self, currency_id: int, quantity: int) -> bool:
        """
        Test if there is enough of currency 'currency_id' such that currency.quantity >= quantity

        Args:
            currency_id: The ID of the currency to test
            quantity: The amount of currency that must be present to return True

        Returns: True if currency.quantity >= quantity, False otherwise
        """

        if currency_id not in self.currencies:
            return False

        return self.currencies[currency_id].quantity >= quantity

    def test_all_purchase(self, item_id: int) -> list[int]:
        """
        Test if the item with item_id can be purchased using any currency and return a list of valid currency IDs

        Args:
            item_id: The ID of the item to test against

        Returns: A list of currency IDs that can be used to purchase the item with item IDs
        """

        costs: dict[int, int] = get_cache()['managers']['ItemManager'].get_costs(item_id)
        return [cur_id for cur_id, value in costs.items() if self.test_currency(cur_id, value)]

    def test_purchase(self, item_id: int, currency_id: int) -> bool:
        """
        Test if the item with id 'item_id' can be purchased using currency with id 'currency_id'.

        Args:
            item_id: The ID of the item to to test the purchase
            currency_id: The ID of the currency to use to test

        Returns: True if the there is a sufficient quantity of currency with id 'currency_id', False otherwise
        """
        return self.test_currency(currency_id, get_cache()['managers']['ItemManager'].get_cost(item_id, currency_id))



