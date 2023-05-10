import copy

import pytest

from game.systems.combat.effect import ResourceEffect
from game.systems.entity.entities import CombatEntity

dummy_entity = CombatEntity(
    id=-1,
    name='dummy'
)


def test_init_trivial():
    re = ResourceEffect(
        "tr_health",
        -10,
        "Some text"
    )

    assert re._resource_name == "tr_health"
    assert re._adjust_quantity == -10
    assert re.trigger_message == "Some text"


perform_cases = [
    ResourceEffect("tr_health", -2)
]


@pytest.mark.parametrize("resource_effect", perform_cases)
def test_perform(resource_effect: ResourceEffect):
    source_tce = copy.deepcopy(dummy_entity)
    target_tce = copy.deepcopy(dummy_entity)
    resource_effect.assign(source_tce, target_tce)

    assert resource_effect._target_entity == target_tce
    assert target_tce.resource_controller[resource_effect._resource_name].value == \
           target_tce.resource_controller[resource_effect._resource_name].max

    resource_effect.perform()

    assert target_tce.resource_controller[resource_effect._resource_name].value == \
           target_tce.resource_controller[resource_effect._resource_name].max + resource_effect._adjust_quantity


fsm_int_cases = [

]


@pytest.mark.parametrize("resource_effect, expected_resource_value", fsm_int_cases)
def test_fsm_int(resource_effect: ResourceEffect, expected_resource_value: int):
    pass


fsm_float_cases = [

]


@pytest.mark.parametrize("resource_effect, expected_resource_value", fsm_float_cases)
def test_fsm_float(resource_effect: ResourceEffect, expected_resource_value: int):
    pass
