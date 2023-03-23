from game.systems.inventory import Inventory


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
