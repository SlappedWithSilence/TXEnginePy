import copy

from game.structures.manager import Manager


class AbilityManager(Manager):

    def __init__(self):
        super().__init__()
        self._ability_manifest: dict[str, any] = {}

    def get_ability(self, ability_name):
        if ability_name not in self._ability_manifest:
            raise ValueError(f"{ability_name} is not a valid ability!")

        return copy.deepcopy(self._ability_manifest[ability_name])

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass