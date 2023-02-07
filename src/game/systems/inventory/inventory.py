from ..item.item import Item


class Inventory:

    def __init__(self, capacity: int = 15, items: list[tuple[int, int]] = None):
        self.capacity: int = capacity
        self.items: list[tuple[int, int]] = items or []

    @property
    def full(self) -> bool:
        return len(self.items) >= self.capacity

    def remove_item(self, item_id, quantity) -> None:
        pass

    def add_item(self, item_id, quantity) -> bool:
        pass
        # Case 1: item already in inventory
            # Case 1a: non-full stack exists
                # Case 1a.a add items into non-full stack.
                    # Case 1a.a.a: Overflow--call add_item on overflowing quantity recursively
                    # Case 1a.a.b: No overflow--terminate
            # Case 1b: only full stacks exists
                # Case 1b.a: Inventory not full--Create new stack. If overflow, call add_item on overflowing quantity recursively
                # Case 1b.b: Inventory full--Prompt user to make space, call add_item again
        # Case 2: item not in inventory
            # Case 2.a: inventory not full--create new stack
                # Case 2.a.a: overflow-- call add_item recursively on overflowing quantity
                # Case 2.a.b: no overflow--terminate
            # Case  2.b: inventory full--prompt user to make space, call add_item again
