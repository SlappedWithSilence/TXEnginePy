import weakref

import game.cache as cache
import game
import game.systems.event.events as events


class Inventory:

    def __init__(self, capacity: int = None, items: list[tuple[int, int]] = None):
        self.capacity: int = capacity
        self.items: list[tuple[int, int]] = items or []

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

        return [idx for idx, stack in enumerate(self.items) if stack[0] == item_id]

    def _all_stacks(self, item_id: int) -> list[tuple[int, int]]:
        if type(item_id) != int:
            raise TypeError(f"item_id must be an int! Got object of type {type(item_id)} instead.")

        return [weakref.proxy(stack) for stack in self.items if stack[0] == item_id]

    def _total_quantity(self, item_id: int) -> int:
        """
        Computes the sum of the quantities of a given item in all available stacks.

        Args:
            item_id: The ID of the item whose sum to compute

        Returns: The total sum quantity of the item in the inventory
        """
        if type(item_id) != int:
            raise TypeError(f"item_id must be an int! Got object of type {type(item_id)} instead.")

        return sum(self._all_stacks(item_id))

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
                if self.items[stack_index][1] > quantity - already_consumed:
                    self.items[stack_index] = item_id, self.items[stack_index][1] - (quantity - already_consumed)
                    return True

                # If the current stack is exactly the size needed, delete it and return True
                elif self.items[stack_index][1] == quantity - already_consumed:
                    del self.items[stack_index]
                    return True

                # If the stack is too small, record its size as consumed and delete it.
                else:
                    already_consumed = already_consumed + self.items[stack_index][1]
                    del self.items[stack_index]

    def __contains__(self, item: int):
        if type(item) != int:
            raise TypeError("Cannot search for non-int in Inventory!")

        for i in self.items:
            if i[0] == item:
                return True

        return False

    def is_collidable(self, item_id: int, quantity: int) -> bool:
        from game.systems.item import item_manager
        """
        Args:
            item_id:
            quantity:

        Returns: True if the user needs to resolve a collision, False otherwise
        """

        remaining_cap: int = self.capacity - len(self.items)
        for stack in self._all_stacks(item_id):
            remaining_cap = remaining_cap + (item_manager.get_instance(item_id).max_quantity - stack[1])

        if quantity > remaining_cap:
            return True

        return False

    def add_item(self, item_id: int, quantity: int) -> None:
        """
        Adds a given quantity of the given item to the inventory. This may add the quantity to an existing stack or
        create a new one. Occasionally, the user may need to choose a stack to drop in order to add the item to the
        inventory.

        Args:
            item_id: The id of the item to add
            quantity: The quantity of the item to add

        Returns: None

        """
        if type(item_id) != int or type(quantity) != int:
            raise TypeError(
                f"item_id and quantity must be of type int! Got type {type(item_id)} and {type(quantity)} instead.")

        game.state_device_controller.add_state_device(events.AddItemEvent(item_id, quantity))
        # Case 1: item already in inventory
        # Case 1a: non-full stack exists
        # Case 1a.a add items into non-full stack.
        # Case 1a.a.a: Overflow--call add_item on overflowing quantity recursively
        # Case 1a.a.b: No overflow--terminate
        # Case 1b: only full stacks exists
        # Case 1b.a: Inventory not full: Create a stack. If overflow, call add_item on overflowing quantity recursively
        # Case 1b.b: Inventory full--Prompt user to make space, call add_item again
        # Case 2: item not in inventory
        # Case 2.a: inventory not full--create new stack
        # Case 2.a.a: overflow-- call add_item recursively on overflowing quantity
        # Case 2.a.b: no overflow--terminate
        # Case  2.b: inventory full--prompt user to make space, call add_item again
