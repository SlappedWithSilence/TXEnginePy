from typing import Union

from ...currency.currency import Currency


class WalletMixin:

    def __init__(self, currencies: Union[list[Currency], dict[str, Currency]]):
        self.currencies: dict[str, Currency] = {}
        if type(currencies) == list:
            for currency in currencies:
                self.currencies[currency.name] = currency

        elif type(currencies) == dict:
            self.currencies = currencies

        else:
            raise TypeError(f"currencies must be list[Currency], dict[str, Currency]! Got {type(currencies)} instead.")


