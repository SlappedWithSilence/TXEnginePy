import pytest

from game.structures.enums import TargetMode
from game.systems.combat import Ability
from game.systems.combat.combat_engine.combat_helpers import \
    calculate_target_resistance, calculate_damage_to_entity
from game.systems.entity.entities import CombatEntity
from game.systems.item.item import Equipment
from game.systems.inventory import EquipmentController
from ..utils import temporary_item, temporary_entity, temporary_ability


def test_target_resistance_trivial():
    """
    Ensure that a basic zero-tag, zero-resistance scenario returns a proper
    zero.
    """
    with temporary_ability([
        Ability(name="temp_ab", description="", on_use="",
                target_mode=TargetMode.SINGLE, damage=1)]
    ) as ability_manager:
        with temporary_entity(
            [CombatEntity(id=-256, name="temp_ce")]
        ) as entity_manager:
            ab_inst = ability_manager.get_instance("temp_ab")
            ce_inst = entity_manager.get_instance(-256)
            calculated_res = calculate_target_resistance(ab_inst, ce_inst)

            # There are no tags on anything, so resistance should be zero.
            assert calculated_res == 0


def test_target_resistance_single_tag():
    """
    For an ability with a single tag and a single piece of armor with resistance
    verify that the total resistance is equal to the resistance of that one
    piece of armor
    """

    with temporary_item([
        Equipment("helm", -256, {-112: 0}, "", "", "head", 0, 0,
                  tags={"tag_a": 0.33})
    ]) as item_manager:
        with temporary_ability([
            Ability(name="temp_ab", description="", on_use="",
                    target_mode=TargetMode.SINGLE, damage=10,
                    tags={"tag_a": None})
        ]) as ability_manager:
            with temporary_entity([
                CombatEntity(id=-256, name="temp_ce",
                             equipment_controller=EquipmentController(
                                 equipment=[-256]
                             ))
            ]) as entity_manager:
                ab_inst = ability_manager.get_instance("temp_ab")
                ce_inst = entity_manager.get_instance(-256)
                calculated_res = calculate_target_resistance(ab_inst, ce_inst)

                assert calculated_res == 0.33


def test_target_resistance_multi_tag():
    """
    For an ability with a single tag and a single piece of armor with resistance
    verify that the total resistance is equal to the resistance of that one
    piece of armor
    """

    with temporary_item([
        Equipment("helm", -256, {-112: 0}, "", "", "head", 0, 0,
                  tags={"tag_a": 0.33}),
        Equipment("chest", -257, {-112: 0}, "", "", "chest", 0, 0,
                  tags={"tag_a": 0.10})
    ]) as item_manager:
        with temporary_ability([
            Ability(name="temp_ab", description="", on_use="",
                    target_mode=TargetMode.SINGLE, damage=10,
                    tags={"tag_a": None})
        ]) as ability_manager:
            with temporary_entity([
                CombatEntity(id=-256, name="temp_ce",
                             equipment_controller=EquipmentController(
                                 equipment=[-256, -257]
                             ))
            ]) as entity_manager:
                ab_inst = ability_manager.get_instance("temp_ab")
                ce_inst = entity_manager.get_instance(-256)
                calculated_res = calculate_target_resistance(ab_inst, ce_inst)

                assert calculated_res == 0.36

def test_dmg_to_trivial():
    """
    Test that an ability with 1 damage deals 1 damage to an entity with zero
    armor resistance and zero tag resistance.
    """

    with temporary_ability([
        Ability(name="temp_ab", description="", on_use="",
                target_mode=TargetMode.SINGLE, damage=1,
                tags={"tag_a": None})
    ]) as ability_manager:
        with temporary_entity([
            CombatEntity(id=-256, name="temp_ce")
        ]) as entity_manager:
            ab_inst = ability_manager.get_instance("temp_ab")
            ce_inst = entity_manager.get_instance(-256)
            calculated_res = calculate_target_resistance(ab_inst, ce_inst)

            assert calculated_res == 0
            assert ce_inst.equipment_controller.total_dmg_resistance == 0

            assert calculate_damage_to_entity(ab_inst, ce_inst) == 1
