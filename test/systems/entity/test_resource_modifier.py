from loguru import logger

from game.systems.entity.entities import CombatEntity
from game.systems.item import item_manager


def test_trivial():
    """
    Test that a modifier can be trivially attached without causing error
    """
    dummy_entity = CombatEntity(0, 0, name="Dummy", id=-110)
    dummy_entity.resource_controller.attach_modifier(item_manager.get_instance(-114))

    dummy_entity.resource_controller.attach_modifier(item_manager.get_instance(-115))
    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", int)) == 1


def test_flat_attach():
    dummy_entity = CombatEntity(0, 0, name="Dummy", id=-110)
    tr_health_initial = dummy_entity.resource_controller.get_max("tr_health")

    dummy_entity.resource_controller.attach_modifier(item_manager.get_instance(-115))
    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", int)) == 1

    assert dummy_entity.resource_controller.get_max("tr_health") == \
           tr_health_initial + item_manager.get_instance(-115).resource_modifiers["tr_health"]


def test_flat_attach_detach():
    dummy_entity = CombatEntity(0, 0, name="Dummy", id=-110)
    tr_health_initial = dummy_entity.resource_controller.get_max("tr_health")

    e_instance = item_manager.get_instance(-115)

    dummy_entity.resource_controller.attach_modifier(e_instance)
    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", int)) == 1

    assert dummy_entity.resource_controller.get_max("tr_health") == \
           tr_health_initial + item_manager.get_instance(-115).resource_modifiers["tr_health"]

    dummy_entity.resource_controller.detach_modifier(e_instance)
    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", int)) == 0
    assert dummy_entity.resource_controller.get_max("tr_health") == dummy_entity.resource_controller.get_base_max(
        "tr_health")


def test_float_attach_detach():
    dummy_entity = CombatEntity(0, 0, name="Dummy", id=-110)
    tr_health_initial = dummy_entity.resource_controller.get_max("tr_health")

    e_instance = item_manager.get_instance(-116)

    dummy_entity.resource_controller.attach_modifier(e_instance)
    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", float)) == 1

    assert dummy_entity.resource_controller.get_max("tr_health") == \
           tr_health_initial + (tr_health_initial * e_instance.resource_modifiers["tr_health"])

    dummy_entity.resource_controller.detach_modifier(e_instance)
    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", float)) == 0
    assert dummy_entity.resource_controller.get_max("tr_health") == dummy_entity.resource_controller.get_base_max(
        "tr_health")


def test_mixed_attach_detach():
    dummy_entity = CombatEntity(0, 0, name="Dummy", id=-110)
    tr_health_initial = dummy_entity.resource_controller.get_max("tr_health")

    e_instance_int = item_manager.get_instance(-115)
    e_instance_float = item_manager.get_instance(-116)

    dummy_entity.resource_controller.attach_modifier(e_instance_int)
    dummy_entity.resource_controller.attach_modifier(e_instance_float)

    expected_max = (
            tr_health_initial +
            (tr_health_initial * e_instance_float.resource_modifiers['tr_health']) +
            e_instance_int.resource_modifiers['tr_health']
    )

    logger.debug(f"Base max: {tr_health_initial}")
    logger.debug(f"Expected max: {expected_max}")

    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", float)) == len(dummy_entity.resource_controller.get_modifiers("tr_health", float)) == 1
    assert dummy_entity.resource_controller.get_max("tr_health") == expected_max

    dummy_entity.resource_controller.detach_modifier(e_instance_float)
    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", float)) == 0
    assert len(dummy_entity.resource_controller.get_modifiers("tr_health", int)) == 1

    assert dummy_entity.resource_controller.get_max("tr_health") == (
            tr_health_initial +
            e_instance_int.resource_modifiers['tr_health']
    )

    dummy_entity.resource_controller.attach_modifier(e_instance_float)
    dummy_entity.resource_controller.detach_modifier(e_instance_int)

    assert dummy_entity.resource_controller.get_max("tr_health") == (
            tr_health_initial +
            (tr_health_initial * e_instance_float.resource_modifiers['tr_health'])
    )

    dummy_entity.resource_controller.detach_modifier(e_instance_float)

    assert dummy_entity.resource_controller.get_max("tr_health") == tr_health_initial

