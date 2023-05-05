class CraftingController:

    def __init__(self, recipe_manifest: list[int] = None, owner=None):
        self.learned_recipes: set[int] = set(recipe_manifest)
        self.owner = owner


