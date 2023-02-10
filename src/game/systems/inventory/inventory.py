import dataclasses

from ... import engine


@dataclasses.dataclass
class Inventory:
    capacity: int = engine.conf.inventory.default_capacity  # Read default value that was loaded from config
    items: list[tuple[int, int]] = dataclasses.field(default_factory=list)

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
        pass
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
