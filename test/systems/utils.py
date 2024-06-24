from contextlib import contextmanager
from typing import Iterable

from game.systems.item import ItemManager
from game.systems.item.item import Item


@contextmanager
def temporary_item(items: Iterable[Item]) -> ItemManager:
    """
    A context manager that temporarily registers a collection of Item objects
    with the global ItemManager instance and then deletes them when the scope
    exits.
    """

    for item in items:
        from game.systems.item import item_manager
        item_manager.register_item(item)

    try:
        from game.systems.item import item_manager
        yield item_manager

    finally:

        # In order to "safely" delete items from the manager, check that the
        # Item registered to that ID has the same name as the temporary Item.
        # This way, an exit that occurs due to a collision doesn't break the
        # Item Manager

        from game.systems.item import item_manager
        for item in items:

            # Make sure item ID exists in manager
            if item_manager.is_id(item.id):

                # Make sure items are the same
                if item_manager.get_ref(item.id).name == item.name:

                    # Delete from the manager permanently
                    del item_manager._manifest[item.id]
