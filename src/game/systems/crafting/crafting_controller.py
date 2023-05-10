from game.systems.crafting import recipe_manager

from loguru import logger


class CraftingController:
    """
    Manages crafting, learning of recipes, and event dispatching for a given Entity.
    """

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, entity) -> None:
        from game.systems.entity.entities import Entity
        if entity is not None and not isinstance(entity, Entity):
            raise TypeError(f"Cannot assign object of type {type(entity)} as owner!")
        self._owner = entity

    def __init__(self, recipe_manifest: list[int] = None, owner=None):
        from game.systems.entity.entities import Entity

        # Detect any non-existent recipe ids in the manifest
        if recipe_manifest is not None:
            for recipe in recipe_manifest:
                if recipe not in recipe_manager:
                    raise ValueError(f"Unknown recipe id! {str(recipe)}")

        self.learned_recipes: set[int] = set(recipe_manifest) if recipe_manifest is not None else set()
        self._owner: Entity = None
        self.owner: Entity = owner

    def can_learn_recipe(self, recipe_id) -> bool:
        """
        Check if the owning Entity meets the requirements to learn the recipe
        """
        return recipe_manager[recipe_id].is_requirements_fulfilled(self.owner)

    def learn_recipe(self, recipe_id: int) -> None:
        """
        Adds a recipe ID to the learned recipes set.

        This method does not prevent and Entity from learning a Recipe even if it does not meet the requirements. To
        check requirements before learning, use a LearnRecipeEvent.
        """
        if recipe_id not in recipe_manager:
            raise ValueError(f"Unknown recipe with ID {recipe_id}")

        if recipe_id in self.learned_recipes:
            logger.warning(f"Recipe with ID {recipe_id} already learned by {self.owner.name}")

        if not self.can_learn_recipe(recipe_id):
            logger.warning(f"{self.owner.name} has learned recipe with ID {recipe_id} without meeting requirements!")

        if recipe_id not in self.learned_recipes:
            self.learned_recipes.add(recipe_id)

    def get_missing_ingredients(self, recipe_id: int) -> list[tuple[int, int]]:
        """
        Check if the owning Entity has sufficient ingredients to execute the recipe and return a list of missing items
        """
        missing_items = []
        for item_id, quantity in recipe_manager[recipe_id].items_in:
            in_inv = self.owner.inventory.total_quantity(item_id)
            if in_inv < quantity:
                missing_items.append((item_id, quantity - in_inv))

        return missing_items

    def has_sufficient_ingredients(self, recipe_id: int) -> bool:
        """
        Check if the owning Entity has sufficient quantity of ingredients to execute the recipe
        """
        return len(self.get_missing_ingredients(recipe_id)) < 1

    def get_max_crafts(self, recipe_id) -> int:
        """
        Get the maximum number of times that this recipe can be crafted.

        The maximum number of crafts is determined by the limiting ingredient, aka whichever ingredient of the recipe
        has the lowest quantity_in_inventory / quantity_demand_from_recipe.
        """

        logger.debug(f"Inventory: {str(self.owner.inventory.items)}")
        logger.debug(f"Recipe: {recipe_manager[recipe_id].name}")
        min_crafts: int = 9999999
        for ingredient_id, ingredient_quantity in recipe_manager[recipe_id].items_in:  # For each ingredient bundle
            in_inv: int = self.owner.inventory.total_quantity(ingredient_id)  # Check amount the user has
            max_crafts: int = int(in_inv / ingredient_quantity)  # Calculate how many bundles are available from the inv
            min_crafts = max_crafts if max_crafts < min_crafts else min_crafts  # Update minimum bundle quantity

        # The maximum number of crafts for the recipe is determined by the ingredient with the lowest relative quantity
        return min_crafts
