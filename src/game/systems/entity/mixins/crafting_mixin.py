from __future__ import annotations

from game.systems.crafting.crafting_controller import CraftingController


class CraftingMixin:
    """
    A mixin that adds support for CraftingController to an entity
    """

    def __init__(self, recipes: list[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.crafting_controller: CraftingController = CraftingController(recipe_manifest=recipes or [], owner=self)
