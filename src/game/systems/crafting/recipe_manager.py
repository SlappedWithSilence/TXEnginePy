from game.structures.manager import Manager
from game.systems.crafting.recpie import Recipe


class RecipeManager(Manager):

    def __init__(self):
        super().__init__()
        self._recipe_manifest: dict[int, Recipe] = {}

    def __contains__(self, item) -> bool:
        return self._recipe_manifest.__contains__(item)

    def __getitem__(self, item) -> Recipe:
        return self._recipe_manifest.__getitem__(item)

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass
