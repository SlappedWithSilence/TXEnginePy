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

    def register_recipe(self, recipe_id: int, recipe: Recipe) -> None:
        """
        Register a Recipe object with the manager.
        """
        if type(recipe_id) != int:
            raise TypeError(f"recipe_id must be an int! Got {type(recipe_id)} instead.")

        if type(recipe) != Recipe:
            raise TypeError(f"recipe must be a Recipe! Got {type(recipe)} instead!")

        if recipe_id in self._recipe_manifest:
            raise ValueError(f"Recipe with id {recipe_id} already exists!")

        if recipe_id != recipe.id:
            raise ValueError(f"Mismatching recipe_id! {recipe_id} != {recipe.id}")

        self._recipe_manifest[recipe_id] = recipe

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass
