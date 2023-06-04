from game.structures.manager import Manager
from game.systems.crafting.recpie import Recipe


class RecipeManager(Manager):

    def __init__(self):
        super().__init__()
        self._manifest: dict[int, Recipe] = {}

    def __contains__(self, item) -> bool:
        return self._manifest.__contains__(item)

    def __getitem__(self, item) -> Recipe:
        return self._manifest.__getitem__(item)

    def register_recipe(self, recipe: Recipe) -> None:
        """
        Register a Recipe object with the manager.
        """
        if type(recipe.id) != int:
            raise TypeError(f"recipe_id must be an int! Got {type(recipe.id)} instead.")

        if type(recipe) != Recipe:
            raise TypeError(f"recipe must be a Recipe! Got {type(recipe)} instead!")

        if recipe.id in self._manifest:
            raise ValueError(f"Recipe with id {recipe.id} already exists!")

        self._manifest[recipe.id] = recipe

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass
