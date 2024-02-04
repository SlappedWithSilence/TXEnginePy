from __future__ import annotations

from game.systems.inventory import inventory_controller as inv


class InventoryMixin:
    """
    A mixin for Entity objects that provides Inventory functionality.
    """

    def __init__(self, inventory: inv.InventoryController = None, **kwargs):
        super().__init__(**kwargs)
        """
        An InventoryController's content may be provided via instance, by tuple, or both.
        """
        self.inventory = inventory or inv.InventoryController()
