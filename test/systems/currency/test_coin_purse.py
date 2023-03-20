import pytest

import game  # Needed to force engine initialization

from game.systems.currency.coin_purse import CoinPurse
from game.systems.currency.currency import Currency
from game.systems.item import Item
from game.systems.currency import currency_manager


def test_init():
    """
    Test that a CoinPurse object can be trivially initialized
    """
    cp = CoinPurse()


def test_currency_acquisition():
    """
    Test that CoinPurse correctly acquires empty Currency objects from the currency_manager
    """

    cp = CoinPurse()
    assert len(cp.currencies.keys()) == len(currency_manager.currencies.keys())
    assert len(cp.currencies) > 0

    for key in currency_manager.currencies:
        assert key in cp.currencies
        assert cp.balance(key) == 0


@pytest.mark.parametrize("cur", currency_manager.currencies.keys())
def test_contains(cur: int | Currency):
    """
    Test that CoinPurse correctly detects the requested currency
    """

    cp = CoinPurse()
    assert cur in cp


contains_bad_cases = [True, False, None, 's', 0.0]


@pytest.mark.parametrize("cur", contains_bad_cases)
def test_contains_bad(cur):
    """
    Test that CoinPurse::__contains__ rejects invalid values
    """

    cp = CoinPurse()

    with pytest.raises(KeyError) as e_info:
        assert cur not in cp


@pytest.mark.parametrize("cur", currency_manager.currencies.keys())
def test_getitem(cur: int | Currency):
    cp = CoinPurse()

    assert len(cp.currencies) > 0

    got = cp[cur]

    assert got is not None
    assert type(got) == Currency


@pytest.mark.parametrize("cur", contains_bad_cases)
def test_getitem_bad(cur: int | Currency):
    """
    Test that CoinPurse::__getitem__ correctly rejects invalid values
    """
    cp = CoinPurse()

    with pytest.raises(KeyError) as e_info:
        assert cur not in cp


def test_balance():
    pass


def test_balance_bad():
    pass


def test_spend():
    pass


def test_spend_bad():
    pass


def test_gain():
    pass


def test_gain_bad():
    pass


def test_test_currency():
    pass


def test_test_currency_bad():
    pass


def test_test_all_purchase():
    pass


def test_test_all_purchase_bad():
    pass


def test_purchase():
    pass


def test_purchase_bad():
    pass