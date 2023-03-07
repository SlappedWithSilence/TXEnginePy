import weakref
from collections import namedtuple

import game.cache as cache
import game
import game.systems.event.events as events
from game.structures.messages import StringContent

Stack = namedtuple('Stack', ['id', 'quantity', 'ref'])


class StackFactory:
    @staticmethod
    def get(item_id: int, item_quantity: int) -> Stack:
        from game.systems.item import item_manager

        return Stack(item_id, item_quantity, item_manager.get_ref(item_id))


class Inventory:

    def __init__(self, capacity: int = None, items: list[tuple[int, int]] = None):
        self.capacity: int = capacity
        self.items: list[Stack] = items or []

        if not self.capacity:
            self.capacity = cache.get_config()["inventory"]["default_capacity"]

    # Private Methods
    def _all_stack_indexes(self, item_id: int) -> list[int]:
        """
        Returns a list of the indexes of all stacks with a matching item_id.

        Args:
            item_id: The ID to look up

        Returns: A list of indexes to valid stacks in the inventory
        """
        if type(item_id) != int:
            raise TypeError(f"item_id must be an int! Got object of type {type(item_id)} instead.")

        return [idx for idx, stack in enumerate(self.items) if stack.id == item_id]

    def _all_stacks(self, item_id: int) -> list[Stack]:
        if type(item_id) != int:
            raise TypeError(f"item_id must be an int! Got object of type {type(item_id)} instead.")

        return [weakref.proxy(stack) for stack in self.items if stack.id == item_id]

    def _total_quantity(self, item_id: int) -> int:
        """
        Computes the sum of the quantities of a given item in all available stacks.

        Args:
            item_id: The ID of the item whose sum to compute

        Returns: The total sum quantity of the item in the inventory
        """
        if type(item_id) != int:
            raise TypeError(f"item_id must be an int! Got object of type {type(item_id)} instead.")

        return sum([s.quantity for s in self._all_stacks(item_id)])

    # Public Methods

    @property
    def full(self) -> bool:
        """
        A property the is True when the inventory has zero remaining slots for new stacks of items
        Returns: True when the inventory has zero remaining slots for new stacks of items, False otherwise

        """
        return len(self.items) >= self.capacity

    def consume_item(self, item_id: int, quantity: int) -> bool:
        """
        Removes a specific quantity of item from the inventory. If there are not enough of the given item, return False
        Args:
            item_id: The id the of the item to consume
            quantity: The quantity of the given item to consume

        Returns: True if the quantity of item_id was consumed, False otherwise

        """
        if type(item_id) != int or type(quantity) != int:
            raise TypeError(
                f"item_id and quantity must be of type int! Got type {type(item_id)} and {type(quantity)} instead.")

        if self._total_quantity(item_id) < quantity:
            return False

        already_consumed: int = 0
        while already_consumed < quantity:

            # If the loop is started over a list of zero stacks, raise an error to avoid an infinite loop
            if len(self._all_stack_indexes(item_id)) < 1:
                raise ValueError(f"Something went wrong while trying to consume item::{item_id}.")

            for stack_index in self._all_stack_indexes(item_id):

                # If the current stack is bigger than needed, adjust its size and return True
                if self.items[stack_index].quantity > quantity - already_consumed:
                    self.items[stack_index] = StackFactory.get(item_id, self.items[stack_index].quantity - (
                            quantity - already_consumed))
                    return True

                # If the current stack is exactly the size needed, delete it and return True
                elif self.items[stack_index].quantity == quantity - already_consumed:
                    del self.items[stack_index]
                    return True

                # If the stack is too small, record its size as consumed and delete it.
                else:
                    already_consumed = already_consumed + self.items[stack_index].quantity
                    del self.items[stack_index]

    def __contains__(self, item: int):
        if type(item) != int:
            raise TypeError("Cannot search for non-int in Inventory!")

        for i in self.items:
            if i.id == item:
                return True

        return False

    def to_options(self) -> list[list[str | StringContent]]:
        results = []

        for stack in self.items:
            results.append(
                [
                    StringContent(value=stack.ref.name, formatting="item_name"),
                    "\t",
                    StringContent(value=f"{stack.quantity}x", formatting="item_quantity")
                ]
            )

        return results

    def drop_stack(self, stack_index: int) -> None:
        """
        Remove a stack from the inventory.

        Args:
            stack_index: The index of the stack within the player's inventory. Zero-indexed.

        Returns: None
        """

        if stack_index >= len(self.items):
            raise ValueError(f"Can't drop stack! {stack_index} is out of range, inventory is of size {len(self.items)}")

        del self.items[stack_index]

    def is_collidable(self, item_id: int, quantity: int) -> bool:
        """
        Args:
            item_id:
            quantity:

        Returns: True if the user needs to resolve a collision, False otherwise
        """

        remaining_cap: int = self.capacity - len(self.items)
        for stack in self._all_stacks(item_id):
            remaining_cap = remaining_cap + (stack.ref.max_quantity - stack.quantity)

        if quantity > remaining_cap:
            return True

        return False

    def new_stack(self, item_id: int, quantity: int, force: bool = False) -> int:
        """
        Creates a new stack in the inventory with the given item_id and item_quantity. If quantity > item.max_stack,
        return the difference.

        Args:
            item_id: The ID of the item to make the stack for
            quantity: the size of the stack
            force: If True, ignore capacity and make new stacks anyways

        Returns: the amount of leftover items that didn't make it into the stack
        """

        if not force and self.full:
            return quantity

        from game.systems.item import item_manager

        leftover = quantity - item_manager.get_instance(item_id).max_quantity

        if leftover >= 0:
            self.items.append(StackFactory.get(item_id, item_manager.get_instance(item_id).max_quantity))
            return leftover

        self.items.append(StackFactory.get(item_id, quantity))
        return 0

    def insert_item(self, item_id: int, quantity: int):
        remaining_quantity = quantity

        for stack in self._all_stacks(item_id):
            if stack.quantity < stack.ref.max_quantity:
                remaining_quantity = remaining_quantity - (stack.ref.max_quantity - stack.quantity)
                stack.quantity = stack.ref.max_quantity

        while remaining_quantity > 0:
            remaining_quantity = self.new_stack(item_id, remaining_quantity, True)
