import pytest

from game.cache import from_cache
from game.systems.combat import Ability
from game.systems.entity.entities import CombatEntity

from game.systems.combat.combat_engine.combat_helpers import calculate_target_resistance


calculate_target_resistance_cases = [

]

@pytest.mark.parametrize("ability_id, target, expected_resistance")
def test_calculate_target_resistance(ability_id: str,
                                     target: CombatEntity,
                                     expected_resistance: float):
    """

    Args:
        ability_id: the ID of the Ability to fetch
        target: An instance of a CombatEntity
        expected_resistance: expected result to compare against

    Returns: None
    """

    instance: Ability = from_cache("managers.AbilityManager").get_instance(ability_id)

    assert calculate_target_resistance(instance, target) == expected_resistance
