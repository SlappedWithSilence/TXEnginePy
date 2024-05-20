import pytest

from game.systems.dialog.dialog import DialogNode


def test_init_trivial():
    node = DialogNode(node_id=0,
                      options={"A choice": -1},
                      text="Text"
                      )

    assert node.node_id == 0
    assert len(node.get_option_text()) == 1
    assert node.text == "Text"
    assert node.visited is False
    assert node.allow_multiple_visits is True
    assert len(node.on_enter) == 0


# is the node visited, are multiple triggers allowed, expected return value
should_trigger_events_cases = [
    [True, True, True],
    [False, False, True],
    [True, False, False],
    [False, True, True]
]


@pytest.mark.parametrize(
    "is_node_visited, multiple_event_triggers, expected",
    should_trigger_events_cases)
def test_should_trigger_events(is_node_visited,
                               multiple_event_triggers,
                               expected):
    node = DialogNode(
        node_id=0,
        options={"A choice": -1},
        text="Text",
        visited=is_node_visited,
        multiple_event_triggers=multiple_event_triggers
    )

    assert node.should_trigger_events() == expected
