from copy import deepcopy

import pytest

from src.game.systems.currency.currency import Currency

currencies = {
    "USD": Currency(-1, "USD", {"cents": 1, "dollars": 100, "k": 100000, "m": 100000000}),
    "Imperial": Currency(-2, "Imperial", {"copper": 1, "silver": 100, "gold": 10000})
}

add_int_quantity_cases = [
    ["USD", [1], 1],
    ["USD", [0], 0],
    ["USD", [1, 1], 2],
    ["USD", [12, 12, 13], 37],
    ["USD", [0, 0, 0, 0], 0],
    ["USD", [1, 100, 0], 101],
    ["USD", [-1], -1],
    ["USD", [-1, 1], 0],
]


@pytest.mark.parametrize("currency, offsets, result", add_int_quantity_cases)
def test_add_int_quantity(currency: str, offsets: list[int], result: int):

    cur = deepcopy(currencies[currency])

    for offset in offsets:
        cur = cur + offset

    assert cur.quantity == result


add_int_str_cases = [
    ["USD", [1], "1 cents"],
    ["USD", [0], "0 cents"],
    ["USD", [1, 1], "2 cents"],
    ["USD", [12, 12, 13], "37 cents"],
    ["USD", [0, 0, 0, 0], "0 cents"],
    ["USD", [1, 100, 0], "1 dollars 1 cents"],
    ["USD", [1111], "10 dollars"],
    ["USD", [100000], "1 k"],
]


@pytest.mark.parametrize("currency, offsets, result", add_int_str_cases)
def test_add_int_str(currency: str, offsets: list[int], result: str):

    cur = deepcopy(currencies[currency])

    for offset in offsets:
        cur = cur + offset

    assert str(cur) == result
