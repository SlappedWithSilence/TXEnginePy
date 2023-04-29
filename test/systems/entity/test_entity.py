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


def test_load():
    j = """
    {
        "class": "Entity",
        "name": "Test",
        "id": 1,
        "attributes": {
            "inventory": [{
                "class": "InventoryController",
                "capacity": 16,
                "manifest": [
                    [-110, 1],
                    [-111, 2]
                ]
            }]
        }
    }
    """

    import json
    j_data = json.loads(j)
    e: Entity = Entity.from_json(j_data)
    assert e
    assert e.name == "Test"
    assert e.id == 1
    assert len(e.inventory) == 2
