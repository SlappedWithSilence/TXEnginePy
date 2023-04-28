import pytest

from game.systems.entity import Entity
from game.systems.inventory import InventoryController


def test_init_trivial():
    e = Entity("Test", -1)
    assert e
    assert e.name == "Test"
    assert e.id == -1
    assert e.equipment_controller is not None
    assert e.inventory is not None
    assert e.coin_purse is not None
    assert e.resource_controller is not None


init_kwargs_cases = [
    {"inventory": InventoryController(16, [(-110, 1)])}
]


@pytest.mark.parametrize("kwargs", init_kwargs_cases)
def test_init_kwargs(kwargs):
    e = Entity("Test", 1, **kwargs)
    assert e
