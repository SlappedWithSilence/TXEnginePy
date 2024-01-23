import pytest

from game.cache import get_config, from_cache
from game.systems.entity.entities import CombatEntity
from systems import TEST_PREFIX

EXPECTED_PRIMARY_RESOURCE = F"{TEST_PREFIX}health"


def fix_primary_resource(func):
    def decorator(*args, **kwargs):
        proper_res_name = get_config()["resources"]["primary_resource"]
        get_config()["resources"]["primary_resource"] = EXPECTED_PRIMARY_RESOURCE
        func(*args, **kwargs)
        get_config()["resources"]["primary_resource"] = proper_res_name

    return decorator


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


is_restorative_items_cases = [
    [-122, True],
    [-123, True],
    [-121, False],
    [-120, False]
]


@pytest.mark.parametrize("item_id, result", is_restorative_items_cases)
def test_is_restorative_item(item_id: int, result: bool):
    inst = from_cache("managers.ItemManager").get_instance(item_id)

    assert CombatEntity._is_restorative_item(inst, EXPECTED_PRIMARY_RESOURCE) == result


restorative_items_cases = [
    [[-120, -121, -119, -122, -123], [-122, -123]],
    [[], []]
]


@pytest.mark.parametrize("inventory_contents, expected_items", restorative_items_cases)
def test_restorative_items(inventory_contents: list[int], expected_items: list[int]):
    proper_res_name = get_config()["resources"]["primary_resource"]
    get_config()["resources"]["primary_resource"] = EXPECTED_PRIMARY_RESOURCE

    entity = _get_intelligent_agent(inventory_contents)
    ri = [item.id for item in entity.restorative_items]

    assert set(ri) == set(expected_items)

    get_config()["resources"]["primary_resource"] = proper_res_name
