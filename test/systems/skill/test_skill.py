from game.systems.skill.skills import Skill

import pytest


def test_init_trivial():
    sk = Skill(name="SomeSkill", id=0)
    assert sk is not None
    assert sk.level == 1
    assert sk.xp == 0
    assert sk.id == 0
    assert sk.name == "SomeSkill"
    assert sk.level_up_limit == sk.initial_level_up_limit
    assert sk.remaining_xp == sk.level_up_limit


def test_remaining_xp():
    pass


def test_xp_ceiling():
    pass


def test_level_up_trivial():
    """
    Tests that level_up correctly handles a single level-up
    """
    pass


level_up_recursive_cases = [

]


@pytest.mark.parametrize("xp", level_up_recursive_cases)
def test_level_up_recursive(xp: int):
    """
    Tests that level_up correctly handles leveling up multiple levels at once
    """
    pass


def test_gain_xp():

    pass
