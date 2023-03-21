import pytest

import game  # Needed to force engine initialization

from game.systems.currency.coin_purse import CoinPurse
from game.systems.currency.currency import Currency
from game.systems.item import Item
from game.systems.currency import currency_manager

from loguru import logger


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


def test_iter_next():
    """
    Verify that CoinPurse::__iter__ and CoinPurse::__next__ are functional

    It is important to verify two properties of CoinPurse's iterable behavior:
        1. CoinPurse correctly traverses its currency list, returning each currency id
        2. A single instance of CoinPurse can be iterated on indefinitely. Each attempted iterator must be correct
    """

    cp = CoinPurse()
    target_iter_len = len(currency_manager.currencies.keys())

    # Iterate upon the same CoinPurse instance twice
    for i in range(2):
        counter = 0  # Track how many elements were seen. You could also just enumerate.

        for cur in cp:  # Actually iterate
            assert cp is not None
            assert cur in cp  # Check if the returned value is meaningful
            counter += 1  # Increment counter

        assert counter == target_iter_len  # Verify we iterated the correct number of times
        logger.info(f"Success! Iterated {target_iter_len} times.")


def test_balance_trivial():
    """
    Trivially check that the currencies in CoinPurse post-init are present and at their initial states
    """

    cp = CoinPurse()
    assert len(cp.currencies) > 0

    for currency in cp:
        assert cp.balance(currency) is not None
        assert cp.balance(currency) == 0


def test_balance_int():
    """
    Test that CoinPurse::balance correctly retrieves values when fed a key of type int
    """
    cp = CoinPurse()
    cp.currencies[0].quantity = 12
    cp.currencies[1].quantity = 100231

    assert cp.balance(0) == 12
    assert cp.balance(1) == 100231


def test_balance_currency():
    """
    Test that CoinPurse::balance correctly retrieves values when fed a key of type Currency
    """
    cp = CoinPurse()
    cp.currencies[0].quantity = 12
    cp.currencies[1].quantity = 100231

    cur0 = currency_manager.to_currency(0, 0)
    cur1 = currency_manager.to_currency(1, 0)

    assert cp.balance(cur0) == 12
    assert cp.balance(cur1) == 100231


balance_bad_cases = [None, "str", -123123, Currency]


@pytest.mark.parametrize("cur", balance_bad_cases)
def test_balance_bad(cur: int | Currency):
    """
    Test that CoinPurse::balance correctly rejects invalid values
    """
    cp = CoinPurse()

    with pytest.raises(KeyError):
        assert cp.balance(cur) == 0


spend_cases_good = [
    [0, 1, 1, 0],
    [0, 100, 50, 50],
    [0, 73, 12, 61],
    [1, 1, 1, 0],
    [1, 51, 2, 49]
]


@pytest.mark.parametrize("cur, start, offset, result", spend_cases_good)
def test_spend(cur: int | Currency, start: int, offset: int, result: int):
    """Test that CoinPurse::spend correctly reduces currency values"""

    cp = CoinPurse()
    assert cp.balance(cur) == 0
    cp.currencies[cur].quantity = start
    assert cp.spend(cur, offset)
    assert cp.balance(cur) == result


spend_cases_false = [
    [0, 0, 1],
    [0, 100, 101],
]


@pytest.mark.parametrize("cur, start, offset", spend_cases_false)
def test_spend_false(cur: int, start: int, offset: int):
    """Test that CoinPurse::spend correctly returns False when presented with an impossible request"""
    cp = CoinPurse()
    assert cp.balance(cur) == 0
    cp.currencies[cur].quantity = start
    assert not cp.spend(cur, offset)


spend_cases_bad = [
    [-12, 0, 0],
    [None, 0, 0],
    [0, 0, None],
    ['a', 100, -101],
]


# TODO: Split this test into multiple smaller tests that explicitly verify that each type of rejection works
@pytest.mark.parametrize("cur, start, offset", spend_cases_bad)
def test_spend_bad(cur: int, start: int, offset: int):
    """Test that CoinPurse::spend correctly rejects invalid values"""
    cp = CoinPurse()

    with pytest.raises((ValueError, KeyError, TypeError)):
        cp.spend(cur, offset)


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