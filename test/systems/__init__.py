from loguru import logger

from game.systems.crafting.recpie import Recipe
from game.systems.currency import currency_manager, Currency
from game.systems.item import Item, item_manager
from game.systems.crafting import recipe_manager

def pre_collect_setup():
    """
    Run some setup code that MUST be run before PyTest attempts to collect tests from the files in this directory and
    its subdirectories.

    This particular pre_collect_setup registering important mock items with global backend systems so that they can be
    initialized within the parameters of parameterized tests.
    """
    logger.info("Setting up test currencies...")

    currency_manager.currencies[-110] = Currency(-110, "USD", {"cents": 1, "dollars": 100})

    currency_manager.currencies[-111] = Currency(-111, "Imperial",
                                                 {
                                                     "bronze": 1,
                                                     "silver": 1000,
                                                     "gold": 1000000
                                                 })

    logger.info("Setting up test items...")
    te1 = Item("Test Item 1", -110, {-110: 2, -111: 3}, "A simple test item", 3)
    te2 = Item("Test Item 2", -111, {-110: 2, -111: 3}, "A simple test item", 3)
    te3 = Item("Test Item 3", -112, {-110: 2, -111: 3}, "A simple test item", 3)
    te4 = Item("Test Item 4", -113, {-110: 3, -111: 4}, "Another test item", 3)

    item_manager.register_item(te1)
    item_manager.register_item(te2)
    item_manager.register_item(te3)
    item_manager.register_item(te4)

    logger.info("Setting up test recipes...")
    tr1 = Recipe(-110, [(-110, 1)], [(-111, 1)])
    tr2 = Recipe(-111, [(-111, 1)], [(-110, 1)])
    tr3 = Recipe(-112, [(-110, 2)], [(-111, 1)])  # Even input, single
    tr4 = Recipe(-113, [(-111, 3)], [(-112, 1)])  # Odd input, single
    tr5 = Recipe(-114, [(-110, 2), (-111, 3), (-112, 1)], [(-113, 2)])  # Mixed input, multi

    recipe_manager.register_recipe(tr1)
    recipe_manager.register_recipe(tr2)
    recipe_manager.register_recipe(tr3)
    recipe_manager.register_recipe(tr4)
    recipe_manager.register_recipe(tr5)


pre_collect_setup()
