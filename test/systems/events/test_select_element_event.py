import pytest
from loguru import logger

from game.cache import from_cache, from_storage
from game.systems.event.select_element_event import SelectElementEvent, SelectElementEventFactory
from game.systems.item import Usable
from systems.events.event_tester import EventTester


def test_trivial_select_element_event():
    """Test that SelectElementEvent can be trivially instantiated"""
    item_ids = [-110, -111, -112]
    e = SelectElementEvent(item_ids,
                           lambda x: int(x),
                           lambda item_id: isinstance(
                               from_cache("managers.ItemManager").get_instance(item_id), Usable),
                           lambda item_id: from_cache("managers.ItemManager").get_instance(item_id).name,
                           "Select an Item"
                           )


def test_functional_select_item_event():
    """
    Test that a linked select element event correctly stores an element
    """
    item_ids = [-110, -111, -112]
    e = SelectElementEvent(item_ids,
                           lambda x: int(x),
                           lambda item_id: item_id < 0,
                           lambda item_id: from_cache("managers.ItemManager").get_instance(item_id).name,
                           "Select an Item"
                           )

    links = e.link()

    tester = EventTester(e, [1], [])
    tester.run_tests()

    assert from_storage(links["selected_element"]) == -111


def test_functional_filter():
    item_ids = [-110, -111, -112]
    e = SelectElementEvent(item_ids,
                           lambda x: int(x),
                           lambda item_id: item_id < -110,
                           lambda item_id: from_cache("managers.ItemManager").get_instance(item_id).name,
                           "Select an Item"
                           )

    links = e.link()

    tester = EventTester(e, [1], [])
    tester.run_tests()

    assert from_storage(links["selected_element"]) == -112


def test_empty_collection():
    """Test that a RuntimeError is correctly thrown when a collection of size 0 is found. """
    item_ids = []

    # Error should be thrown on instantiation
    with pytest.raises(RuntimeError):
        e = SelectElementEvent(item_ids,
                               lambda x: int(x),
                               lambda item_id: item_id < -110,
                               lambda item_id: from_cache("managers.ItemManager").get_instance(item_id).name,
                               "Select an Item"
                               )


def test_empty_filtered_collection():
    """Test that a RuntimeError is correctly thrown when a collection is filtered down to size of 0"""

    item_ids = [-110, -111, -112]
    e = SelectElementEvent(item_ids,
                           lambda x: int(x),
                           lambda item_id: item_id == 0,
                           lambda item_id: from_cache("managers.ItemManager").get_instance(item_id).name,
                           "Select an Item"
                           )

    links = e.link()

    # The error should be thrown later than the previous test, this time during execution of state logic
    with pytest.raises(RuntimeError):
        tester = EventTester(e, [1], [])
        tester.run_tests()


def test_factory_ability_selection_functional():
    """Test that the SelectElementEventFactory's get_select_ability_event function returns a functional event"""
    e = SelectElementEventFactory.get_select_ability_event(from_cache("managers.EntityManager").get_instance(-110))

    links = e.link()

    tester = EventTester(e, [1], [], show_frames=True)
    tester.run_tests()

    assert from_storage(links["selected_element"]) == "Test Ability 2"


def test_factory_ability_selection_functional_castable():
    """Test that the SelectElementEventFactory's get_select_ability_event function returns a functional event when
    configured to filter for 'castable' abilities only.
    """

    # Modify entity to make Test Ability 2 not 'castable'
    entity = from_cache("managers.EntityManager").get_instance(-110)  # Get a copy of the entity
    entity.resource_controller.get_instance("tr_health").adjust(-1.0)  # Set health to 0
    assert entity.resource_controller.get_value("tr_health") == 0  # Verify health is now 0
    assert from_cache("managers.AbilityManager").get_instance("Test Ability 2").costs["tr_health"] > 0  # Verify ta_2 costs more than 0 health

    event = SelectElementEventFactory.get_select_ability_event(entity, must_select=True, only_requirements_met=True)

    links = event.link()

    tester = EventTester(event, [1], [], show_frames=True)
    tester.run_tests()

    assert from_storage(links["selected_element"]) == "Test Ability 3"
