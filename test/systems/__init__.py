from loguru import logger

from game.structures.enums import TargetMode
from game.systems.crafting.recipe import Recipe
from game.systems.currency import currency_manager, Currency
from game.systems.entity import Resource
from game.systems.entity.entities import CombatEntity
from game.systems.item import Item, item_manager, Equipment, Usable
from game.systems.crafting import recipe_manager
from game.systems.entity import entity_manager
from game.systems.combat import ability_manager, Ability
from game.systems.requirement.requirements import ResourceRequirement


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

    te11 = Usable("Test Usable 1", -120, {-110: 2}, "", requirements=[ResourceRequirement("tr_health", 2)])
    te12 = Usable("Test Usable 1", -121, {-110: 5}, "", requirements=[ResourceRequirement("tr_health", 5)])

    item_manager.register_item([te1, te2, te3, te4, te5, te6, te7, te8, te9, te10, te11, te12])

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
    ta_1 = Ability(name="Test Ability 1", description="ta_1", on_use="ta_1 used", target_mode=TargetMode.SINGLE)
    ta_2 = Ability(name="Test Ability 2", description="ta_2", on_use="ta_2 used", target_mode=TargetMode.SINGLE,
                   costs={"tr_health": 1})
    ta_3 = Ability(name="Test Ability 3", description="ta_3", on_use="ta_3 used", target_mode=TargetMode.SINGLE,
                   costs={"tr_stamina": 2})
    ability_manager.register_ability(ta_1)
    ability_manager.register_ability(ta_2)
    ability_manager.register_ability(ta_3)

    logger.info("Setting up test entities...")
    te_ally_1 = CombatEntity(name="Test Ally", id=-110, turn_speed=2)
    te_ally_1.ability_controller.learn("Test Ability 1")
    te_ally_1.ability_controller.learn("Test Ability 2")
    te_ally_1.ability_controller.learn("Test Ability 3")
    te_enemy_1 = CombatEntity(name="Test Enemy", id=-111, turn_speed=3)

    entity_manager.register_entity(te_ally_1)
    entity_manager.register_entity(te_enemy_1)


pre_collect_setup()
