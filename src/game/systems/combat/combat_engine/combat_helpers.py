from game.systems.combat import Ability
from game.systems.entity.entities import CombatEntity


def calculate_target_resistance(ability: Ability, target: CombatEntity) -> float:
    """
    For a given Ability and target, calculate the resistance value of the target

    Args:
        ability: The Ability to check against
        target: The CombatEntity to check against

    Returns: A float representing the resistance of the target
    """
    if not isinstance(ability, Ability):
        raise TypeError(f"Expected ability to be of type Ability, got "
                        f"{type(ability)} instead!")

    if not isinstance(target, CombatEntity):
        raise TypeError("Expected target to be of type CombatEntity, got "
                        f"{type(target)} instead!")

    if not isinstance(ability.tags, set):
        raise TypeError("ability.tags should be of type Set! Got type"
                        f"{type(ability.tags)} instead!")

    # TODO: Implement