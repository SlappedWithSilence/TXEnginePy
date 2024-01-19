import pytest

from game.systems.entity.entities import CombatEntity


def _get_intelligent_agent(inventory_contents: list[int] = None, abilities: list[str] = None,
                           resource_values: dict[str, int] = None) -> CombatEntity:
    entity = CombatEntity(name="Test Intelligent Agent", abilities=abilities, naive=False, id=-1)

    if inventory_contents:
        for item_id in inventory_contents:
            entity.inventory.insert_item(item_id, 1)

    if resource_values:
        for resource in resource_values:
            entity.resource_controller[resource].value = resource_values[resource]

    return entity


def test_instantiation():
    _get_intelligent_agent()


restorative_items_cases = [
    [[], []],
    [[], []]
]


@pytest.mark.parametrize("inventory_contents, expected_items", restorative_items_cases)
def test_restorative_items(inventory_contents: list[int], expected_items: list[int]):
    entity = _get_intelligent_agent(inventory_contents)
    ri = [item.id for item in entity.restorative_items]

    for item_id in expected_items:
        assert item_id in ri
