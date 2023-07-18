import pytest

from game.cache import cache_element, from_cache
from game.systems.combat.combat_engine.combat_engine import CombatEngine
from game.systems.entity.entities import CombatEntity


def get_test_allies() -> list[int]:
    """
    Get a default list of generic ally CombatEntity objects.
    """

    return [
        -110
    ]


def get_test_enemies() -> list[int]:
    """
    Get a default list of generic enemy CombatEntity objects.
    """
    return [
        -111
    ]


def get_generic_combat_instance() -> CombatEngine:
    """
    Return a fresh instance of a generic (totally-default) CombatEngine.
    """
    return CombatEngine(get_test_allies(), get_test_enemies())


def test_init_trivial():
    """
    Test that CombatEngine can be instantiated without generating an Error.
    """
    assert get_generic_combat_instance()


def test_self_cache():
    """
    Test that a CombatEngine instance correctly caches a reference to itself on instantiation and purges the reference
    when it is deleted.
    """

    # Ensure that there is no cached combat
    cache_element("combat", None)
    assert from_cache("combat") is None

    # Spawn a new combat session the check that it got cached
    engine = get_generic_combat_instance()
    assert from_cache("combat") == engine

    # Terminate the combat session and verify that it isn't cached anymore
    engine.state_data[engine.States.TERMINATE.value]['logic'](None)
    assert from_cache("combat") is None


def test_duplicate_combats():
    """
    Test that duplicate combat sessions correctly throw an error when spawned
    """

    engine = get_generic_combat_instance()
    with pytest.raises(RuntimeError):
        engine2 = get_generic_combat_instance()

