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


perform_cases_single = [
    ResourceEffect("tr_health", -2),
    ResourceEffect("tr_health", 3),
    ResourceEffect("tr_stamina", -11),
    ResourceEffect("tr_stamina", 4),
    ResourceEffect("tr_mana", -4),
    ResourceEffect("tr_mana", 6),
]


@pytest.mark.parametrize("resource_effect", perform_cases_single)
def test_perform_single(resource_effect: ResourceEffect):
    res_name = resource_effect._resource_name
    source_tce = copy.deepcopy(dummy_entity)
    target_tce = copy.deepcopy(dummy_entity)
    RES_START_VALUE = 15
    target_tce.resource_controller[res_name].value = RES_START_VALUE
    resource_effect.assign(source_tce, target_tce)

    assert resource_effect._target_entity == target_tce
    assert target_tce.resource_controller[resource_effect._resource_name].value == RES_START_VALUE

    resource_effect.perform()

    assert target_tce.resource_controller[resource_effect._resource_name].value == \
           RES_START_VALUE + resource_effect._adjust_quantity


perform_cases_multiple = [
    [[ResourceEffect("tr_health", -2), ResourceEffect("tr_health", 3)],
     {"tr_health": 1}],
    [[ResourceEffect("tr_stamina", -11), ResourceEffect("tr_stamina", 4)],
     {"tr_stamina": -7}],
    [[ResourceEffect("tr_mana", -4), ResourceEffect("tr_mana", 6)],
     {"tr_mana": 2}],
    [[ResourceEffect("tr_mana", -4), ResourceEffect("tr_health", 6)],
     {"tr_mana": -4, "tr_health": 6}],
    [[ResourceEffect("tr_mana", -4), ResourceEffect("tr_mana", 6), ResourceEffect("tr_stamina", 3)],
     {"tr_mana": 2, "tr_stamina": 3}]
]


@pytest.mark.parametrize("resource_effects, net_res_changes", perform_cases_multiple)
def test_perform_multiple(resource_effects: list[ResourceEffect], net_res_changes: dict[str, int]):
    """
    Test that multiple consecutive ResourceEffect triggers resolve correctly.
    """

    # Set up source and target entities
    source_tce = copy.deepcopy(dummy_entity)
    target_tce = copy.deepcopy(dummy_entity)

    RESOURCE_BASE_VALUE = 15  # The value that each resource will start at
    for res in net_res_changes:
        target_tce.resource_controller[res].value = RESOURCE_BASE_VALUE

    # Execute effects in series and measure correctness at each step
    for effect in resource_effects:
        res_name = effect._resource_name
        starting_res_value = target_tce.resource_controller[res_name].value  # Value before execution
        effect.assign(source_tce, target_tce)
        effect.perform()  # Execution
        assert target_tce.resource_controller[res_name].value == starting_res_value + effect._adjust_quantity  # Verify

    # For each resource modified, ensure that its final value conforms with the predicted differences
    for res in net_res_changes:
        assert target_tce.resource_controller[res].value - RESOURCE_BASE_VALUE == net_res_changes[res]


fsm_int_cases = [

]


# Interface not finalized, so tests not written
@pytest.mark.parametrize("resource_effect, expected_resource_value", fsm_int_cases)
def test_fsm_int(resource_effect: ResourceEffect, expected_resource_value: int):
    pass


fsm_float_cases = [

]


# Interface not finalized, so tests not written
@pytest.mark.parametrize("resource_effect, expected_resource_value", fsm_float_cases)
def test_fsm_float(resource_effect: ResourceEffect, expected_resource_value: int):
    pass
