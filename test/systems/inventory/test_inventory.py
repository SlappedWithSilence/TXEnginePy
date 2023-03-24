import pytest

from game.systems.inventory import Inventory
from game.systems.item import item_manager


def test_init():
    """Trivially initialize an Inventory object"""
    iv = Inventory()

    assert iv.capacity > 0
    assert iv.size == 0
    assert not iv.full


def test_full():
    """Test that Inventory::full correctly returns True when all stacks are created"""
    iv = Inventory()

    assert iv.capacity > 0

    for i in range(iv.capacity):
        assert iv.new_stack(-110, 1) == 0

    assert iv.full


def test_size():
    """Trivially test that Inventory::size increments as stacks are created"""
    iv = Inventory()

    assert iv.size == 0

    for i in range(iv.capacity):
        iv.new_stack(-110, 1)
        assert iv.size == i + 1


def test_consume_item_present():
    """
    Test that Inventory::consume_item correctly decrements a stack of items and returns True

    Flow:
        - Make a new stack of size 2
        - Consume 1 item
        - Verify stack is of size 1
    """
    iv = Inventory()

    assert iv.new_stack(-110, 2) == 0
    assert iv.size == 1
    assert iv.consume_item(-110, 1)
    assert iv.size == 1


def test_consume_item_last_present():
    """
    Test that Inventory::consume_item handles stacks with exact sizes

    Flow:
        - Make a new stack of size 2
        - Consume 2 items
        - Verify that the stack fully consumed and no longer exists
    """
    iv = Inventory()

    assert iv.new_stack(-110, 2) == 0
    assert iv.size == 1
    assert iv.consume_item(-110, 2)
    assert iv.size == 0


def test_consume_item_multiple_stacks():
    """
    Test that Inventory::consume_item can consume items from more than one stack.

    Flow:
        - Make a stack of size 3
        - Make a stack of size 2
        - Consume 4 items
        - Verify that only one stack remains and is of size 1
    """

    iv = Inventory()
    assert iv.new_stack(-110, 3) == 0
    assert iv.new_stack(-110, 2) == 0
    assert iv.size == 2
    assert iv.consume_item(-110, 4)
    assert iv.size == 1
    assert iv.total_quantity(-110) == 1


def test_consume_item_multiple_stacks_exact():
    """
    Test that Inventory::consume_item consumes and deletes multiple stacks if exactly the right quantity of items are
    present between them.

    Flow:
        - Make a stack of size 3
        - Make a stack of size 2
        - Consume 5 items
        - Verify that there are 0 remaining stacks
    """

    iv = Inventory()
    iv.new_stack(-110, 3)
    iv.new_stack(-110, 2)
    assert iv.size == 2
    assert iv.consume_item(-110, 5)
    assert iv.size == 0


def test_consume_item_no_stacks():
    """
    Test that Inventory::consume_item doesn't modify the inventory if there are no stacks
    """
    iv = Inventory()
    assert iv.size == 0
    assert not iv.consume_item(-110, 1)


def test_consume_item_not_enough_stacks():
    """
    Test that Inventory::consume_item doesn't modify the inventory if there are not enough items
    between the stacks
    """
    iv = Inventory()
    assert iv.size == 0

    iv.new_stack(-110, 2)
    assert iv.size == 1
    assert iv.total_quantity(-110) == 2
    assert not iv.consume_item(-110, 3)
    assert iv.size == 1
    assert iv.total_quantity(-110) == 2


def test_consume_item_mixed():
    """
    Test that Inventory::consume_item only modifies stacks that contain the specified Item

    Flow:
        - Make a stack of -110 x3
        - Make a stack of -111 x3
        - Make a stack of -112 x3
        - Verify inventory size of 3
        - Consume -110 x1
        - Verify inventory size of 3
        - Consume -112 x3
        - Verify inventory size of 2
        - Verify -110 quantity of 1
        - Verify -112 quantity of 3
        - Consume -112 x2
        - Verify inventory size of 2
        - Verify -112 quantity of 1
        - Verify -110 quantity of 2
    """

    iv = Inventory()
    iv.new_stack(-110, 3)
    iv.new_stack(-111, 3)
    iv.new_stack(-112, 3)

    assert iv.size == 3
    assert iv.consume_item(-110, 1)
    assert iv.size == 3
    assert iv.consume_item(-111, 3)
    assert iv.size == 2
    assert iv.total_quantity(-110) == 2
    assert iv.total_quantity(-112) == 3
    assert iv.consume_item(-112, 2)
    assert iv.size == 2
    assert iv.total_quantity(-112) == 1
    assert iv.total_quantity(-110) == 2


def test_consolidate_trivial():
    iv = Inventory()

    iv.new_stack(-110, 1)
    iv.new_stack(-110, 1)
    assert iv.size == 2
    assert iv.total_quantity(-110) == 2
    iv._consolidate_stacks()
    assert iv.size == 1
    assert iv.total_quantity(-110) == 2


def test_consolidate_mixed():
    iv = Inventory()

    iv.new_stack(-110, 1)
    iv.new_stack(-110, 1)
    iv.new_stack(-111, 2)
    iv.new_stack(-112, 2)
    iv.new_stack(-110, 2)
    iv.new_stack(-111, 2)

    assert iv.size == 6
    assert iv.total_quantity(-110) == 4
    assert iv.total_quantity(-111) == 4
    assert iv.total_quantity(-112) == 2

    iv._consolidate_stacks()
    assert iv.size == 5
    assert iv.total_quantity(-110) == 4
    assert iv.total_quantity(-111) == 4
    assert iv.total_quantity(-112) == 2


# TODO: Add cases
consume_item_mixed_split_stacks_cases = [
    [{-110: 7, -111: 4, -112: 1}, [(-110, 4), (-111, 2)], {-110: 3, -111: 2, -112: 1}, 3]
]


@pytest.mark.parametrize("start, seq, end, size", consume_item_mixed_split_stacks_cases)
def test_consume_item_mixed_split_stacks(start: dict[int, int], seq: list[tuple[int, int]], end: dict[int, int],
                                         size: int):
    iv = Inventory()

    for item_id in start:
        iv.insert_item(item_id, start[item_id])

    for sequence in seq:
        assert iv.consume_item(*sequence)

    for item_id in end:
        assert iv.total_quantity(item_id) == end[item_id]

    assert iv.size == size, str(iv.to_options())


contains_cases = [
    [[(-110, 1)], -110, True],  # Trivial int true
    [[], -110, False],  # Trivial false
    [[(-110, 1)], item_manager.get_instance(-110), True],  # Trivial item true
    [[], item_manager.get_instance(-110), False],  # Trivial item false
    [[(-110, 1)], -111, False],  # Missing stack, int
    [[(-110, 1)], item_manager.get_instance(-111), False],  # Missing stack, item
    [[(-110, 1), (-111, 1)], item_manager.get_instance(-111), True],  # Mixed stacks, item
    [[(-110, 1), (-111, 1)], -111, True],  # Mixed stacks, int
    [[(-110, 1), (-111, 1)], item_manager.get_instance(-112), False],  # Missing stack, mixed, item
    [[(-110, 1), (-111, 1)], -112, False],  # Missing stack, mixed, int
]


@pytest.mark.parametrize("items, search_term, result", contains_cases)
def test_contains(items: list[tuple[int, int]], search_term, result: bool):
    iv = Inventory()

    for pair in items:
        iv.new_stack(*pair)

    assert (search_term in iv) == result
