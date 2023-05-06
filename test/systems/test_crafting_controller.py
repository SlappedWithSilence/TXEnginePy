from game.systems.crafting.crafting_controller import CraftingController

import pytest

from game.systems.entity import Entity
from game.systems.inventory import InventoryController


def test_init_trivial():
    cc = CraftingController()
    assert cc is not None


manifest_cases = [
    [],
    [1],
    [0, 1, 2, 3, 4]
]


@pytest.mark.parametrize("manifest", manifest_cases)
def test_manifest(manifest: list[int]):
    cc = CraftingController(manifest)

    for recipe in manifest:
        assert recipe in cc.learned_recipes


def test_owner():
    e = Entity(name="Crafty Boy",
               id=1,
               inventory=InventoryController(
                   items=[
                    (-110, 1),
                    (-111, 2)
                   ]
                 )
               )
