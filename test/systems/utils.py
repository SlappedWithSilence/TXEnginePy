from contextlib import contextmanager
from typing import Iterable

from game.systems.item import ItemManager
from game.systems.item.item import Item
from game.systems.entity import EntityManager
from game.systems.entity.entities import CombatEntity


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


@contextmanager
def temporary_entity(entities: Iterable[CombatEntity]) -> EntityManager:
    """
    A context manager that temporarily registers a collection of Entity objects
    with the global EntityManager instance and then deletes them when the scope
    exits.
    """

    for entity in entities:
        from game.systems.entity import entity_manager
        entity_manager.register_entity(entity)

    try:
        from game.systems.entity import entity_manager
        yield entity_manager

    finally:

        # In order to "safely" delete items from the manager, check that the
        # Item registered to that ID has the same name as the temporary Item.
        # This way, an exit that occurs due to a collision doesn't break the
        # Item Manager

        from game.systems.entity import entity_manager
        for entity in entities:

            # Make sure item ID exists in manager
            if entity_manager.is_id(entity.id):

                # Make sure items are the same
                if entity_manager.get_instance(entity.id).name == entity.name:
                    # Delete from the manager permanently
                    del entity_manager._manifest[entity.id]
