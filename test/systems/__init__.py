from loguru import logger

from game.systems.crafting.recipe import Recipe
from game.systems.currency import currency_manager, Currency
from game.systems.entity import Resource
from game.systems.item import Item, item_manager, Equipment
from game.systems.crafting import recipe_manager


def pre_collect_setup():
    """
    Run some setup code that MUST be run before PyTest attempts to collect tests from the files in this directory and
    its subdirectories.

    This particular pre_collect_setup registering important mock items with global backend systems so that they can be
    initialized within the parameters of parameterized tests.
    """
    logger.info("Setting up test currencies...")

    currency_manager.register_currency(Currency(-110, "USD", {"cents": 1, "dollars": 100}))

    currency_manager.register_currency(Currency(-111, "Imperial",
                                                {
                                                    "bronze": 1,
                                                    "silver": 1000,
                                                    "gold": 1000000
                                                }))

    logger.info("Setting up test items...")
    te1 = Item("Test Item 1", -110, {-110: 2, -111: 3}, "A simple test item", 3)
    te2 = Item("Test Item 2", -111, {-110: 2, -111: 3}, "A simple test item", 3)
    te3 = Item("Test Item 3", -112, {-110: 2, -111: 3}, "A simple test item", 3)
    te4 = Item("Test Item 4", -113, {-110: 3, -111: 4}, "Another test item", 3)

    te5 = Equipment("Test Equipment 1", -114, {-110: 1}, "", "ring", 0, 0)
    te6 = Equipment("Test Equipment 2", -115, {-110: 1}, "", "chest", 0, 0, resource_modifiers={"tr_health": 3})
    te7 = Equipment("Test Equipment 3", -116, {-110: 1}, "", "legs", 0, 0, resource_modifiers={"tr_health": 0.1})
    te8 = Equipment("Test Equipment 3", -117, {-110: 1}, "", "legs", 0, 0, resource_modifiers={"tr_health": 0.1})
    te9 = Equipment("Test Equipment 3", -118, {-110: 1}, "", "legs", 0, 0, resource_modifiers={"tr_health": -1})
    te10 = Equipment("Test Equipment 3", -119, {-110: 1}, "", "legs", 0, 0, resource_modifiers={"tr_health": -0.25})

    item_manager.register_item([te1, te2, te3, te4, te5, te6, te7, te8, te9, te10])

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

    logger.info("Setting up resources...")
    from game.systems.entity import resource_manager
    tr_health = Resource('tr_health', 40, 'Needed to live')
    tr_sta = Resource('tr_stamina', 35, 'Tired without it')
    tr_mana = Resource('tr_mana', 50, 'Magic-dependant')

    resource_manager.register_resource(tr_sta)
    resource_manager.register_resource(tr_mana)
    resource_manager.register_resource(tr_health)

    logger.info("Setting up test abilities...")
    # Set some abilities

    logger.info("Setting up test entities...")
    # Set some entities


pre_collect_setup()
