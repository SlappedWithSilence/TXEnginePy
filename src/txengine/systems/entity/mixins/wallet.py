from typing import Union


class WalletMixin:

    def __init__(self, currencies: dict[str, int]):
        self.currencies = currencies
