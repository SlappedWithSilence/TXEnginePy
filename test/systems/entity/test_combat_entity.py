from game.systems.entity.entities import CombatEntity

import pytest


def test_init_trivial():
    ce = CombatEntity(name="CombatEntity", id=-1)


init_kwargs_cases = [
    {"name": "Proto Combat Entity",
     "id": 9999,
     },
    {"name" : "TCE",
     "id" : 1,
     "xp_yield" : 10,
     "turn_speed" : 2,
     }
]


@pytest.mark.parametrize("kwargs", init_kwargs_cases)
def test_init_kwargs(kwargs):
    ce = CombatEntity(**kwargs)

    for kw in kwargs:
        if hasattr(ce, kw):
            assert getattr(ce, kw) == kwargs[kw]