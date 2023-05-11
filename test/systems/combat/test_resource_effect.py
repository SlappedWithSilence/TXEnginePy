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


perform_cases_single_int = [
    ResourceEffect("tr_health", -2),
    ResourceEffect("tr_health", 3),
    ResourceEffect("tr_stamina", -11),
    ResourceEffect("tr_stamina", 4),
    ResourceEffect("tr_mana", -100),
    ResourceEffect("tr_mana", 600),
]


@pytest.mark.parametrize("resource_effect", perform_cases_single_int)
def test_perform_single_int(resource_effect: ResourceEffect):
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
           min(max(RES_START_VALUE + resource_effect._adjust_quantity, 0), target_tce.resource_controller[res_name].max)


perform_cases_multiple_int = [
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


@pytest.mark.parametrize("resource_effects, net_res_changes", perform_cases_multiple_int)
def test_perform_multiple_int(resource_effects: list[ResourceEffect], net_res_changes: dict[str, int]):
    """
    Test that multiple consecutive ResourceEffect triggers resolve correctly.
    """

    # Set up source and target entities
    source_tce = copy.deepcopy(dummy_entity)
    target_tce = copy.deepcopy(dummy_entity)

    RESOURCE_BASE_VALUE = 15  # The value that each resource will start at
    for res in net_res_changes:
        target_tce.resource_controller[res].value = RESOURCE_BASE_VALUE

    for res in net_res_changes:
        assert target_tce.resource_controller[res].value == RESOURCE_BASE_VALUE

    # Execute effects in series and measure correctness at each step
    for effect in resource_effects:
        res_name = effect._resource_name
        starting_res_value = target_tce.resource_controller[res_name].value  # Value before execution
        effect.assign(source_tce, target_tce)
        effect.perform()  # Execution
        assert target_tce.resource_controller[res_name].value == \
               min(max(0, starting_res_value + effect._adjust_quantity), target_tce.resource_controller[res_name].max)

    # For each resource modified, ensure that its final value conforms with the predicted differences
    for res in net_res_changes:
        assert target_tce.resource_controller[res].value - RESOURCE_BASE_VALUE == net_res_changes[res]


perform_cases_single_float = [
    ResourceEffect("tr_health", 0.1),  # +10%
    ResourceEffect("tr_health", -0.1),  # -10%
    ResourceEffect("tr_stamina", -0.33),  # -33%
    ResourceEffect("tr_stamina", 0.3),  # +30%
    ResourceEffect("tr_mana", -1.0),  # -100%  # Tests min enforcement
    ResourceEffect("tr_mana", 1.0),  # + 100% : Tests max enforcement
]


@pytest.mark.parametrize("resource_effect", perform_cases_single_float)
def test_perform_single_float(resource_effect: ResourceEffect):
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
           min(
               max(
                   0,
                   RES_START_VALUE + (RES_START_VALUE * resource_effect._adjust_quantity)
               ),
               target_tce.resource_controller[res_name].max
           )


perform_cases_multiple_float = [
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


@pytest.mark.parametrize("resource_effects, net_res_changes", perform_cases_multiple_float)
def test_perform_multiple_float(resource_effects: list[ResourceEffect], net_res_changes: dict[str, int]):
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
