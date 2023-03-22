import pytest
from loguru import logger


def setup_module():
    logger.info("Setting up Currency tests...")
    import game  # Needed to force engine initialization
    from game.systems.currency import currency_manager
    from game.systems.currency import Currency

    currency_manager.currencies[-110] = Currency(-110, "USD", {"cents": 1, "dollars": 100})

    currency_manager.currencies[-111] = Currency(-111, "Imperial",
                                                 {
                                                     "bronze": 1,
                                                     "silver": 1000,
                                                     "gold": 1000000
                                                 })

    from game.systems.item import item_manager, Item

    te = Item("Test Item", -110, {-110: 2, -111: 3}, "A simple test item", 1)
    item_manager.register_item(te)
    assert item_manager.get_name(-110) == "Test Item", "Failed to register test item"
    logger.info(f"Inserted test item: {str(item_manager.get_ref(-110))}")


def teardown_module():
    """revert the state """
    logger.info("Tearing down Currency tests...")
    from game.systems.currency import currency_manager
    currency_manager.currencies.pop(-110)
    currency_manager.currencies.pop(-111)

    from game.systems.item import item_manager
    item_manager._master_item_manifest.pop(-110)
