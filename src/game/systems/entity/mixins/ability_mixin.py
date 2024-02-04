from __future__ import annotations

from game.systems.combat.ability_controller import AbilityController


class AbilityMixin:
    """
    A mixin that grants an Entity the capacity to learn Abilities
    """

    def __init__(self, abilities: list[str] = None, ability_controller=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ability_controller = ability_controller or AbilityController()
        if abilities is not None:
            for ability in abilities:
                self.ability_controller.learn(ability)
