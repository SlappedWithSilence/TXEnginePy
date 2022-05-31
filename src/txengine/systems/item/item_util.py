from typing import Union
from copy import deepcopy
from weakref import proxy

from ...cache import item_map
from .item import Item


def item_name(item_id: int) -> Union[str, None]:
    """Returns the name of the item with the given id"""

    if item_id not in item_map:
        raise ValueError(f"No item with id {item_id}!")

    else:
        return item_map[item_id].name


def deep_copy(item_id: int) -> Union[Item, None]:
    """Returns a deep copy of the item with the given id"""

    if item_id not in item_map:
        raise ValueError(f"No item with id {item_id}!")

    return deepcopy(item_map[item_id])


def reference(item_id) -> Union[Item, None]:
    """Returns a weakref to the item with given id"""

    if item_id not in item_map:
        raise ValueError(f"No item with id {item_id}!")

    return proxy(item_map[item_id])

