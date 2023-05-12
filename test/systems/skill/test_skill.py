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

