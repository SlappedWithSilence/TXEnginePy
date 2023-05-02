import copy

from game.structures.manager import Manager
from game.systems.combat.ability import Ability


class AbilityManager(Manager):

    def __init__(self):
        super().__init__()
        self._ability_manifest: dict[str, Ability] = {}

    def is_ability(self, ability_name: str) -> bool:
        return ability_name in self._ability_manifest

    def get_ability(self, ability_name) -> Ability:
        if ability_name not in self._ability_manifest:
            raise ValueError(f"{ability_name} is not a valid ability!")

        return copy.deepcopy(self._ability_manifest[ability_name])

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass
