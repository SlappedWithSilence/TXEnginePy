from game.cache import from_cache, from_storage
from game.systems.event.select_element_event import SelectElementEvent
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
    item_ids = [-110, -111, -112]
    e = SelectElementEvent(item_ids,
                           lambda x: int(x),
                           lambda item_id: item_id < 0,
                           lambda item_id: from_cache("managers.ItemManager").get_instance(item_id).name,
                           "Select an Item"
                           )

    links = e.link()

    tester = EventTester(e, [0], [])
    tester.run_tests()

    assert from_storage(links["selected_element"]) == -110
