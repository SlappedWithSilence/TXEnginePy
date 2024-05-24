import pytest

from game.systems.dialog.dialog import DialogNode, Dialog


def test_init_trivial():

    node = DialogNode(node_id=0,
                      options={"A choice": -1},
                      text="Text"
                      )
    d = Dialog(dialog_id=0, nodes=[node])  # Attach node to a Dialog
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


def test_invalid_option_target():
    # There is no node in the Dialog with id=3, so an error must be thrown
    node = DialogNode(
        node_id=0,
        options={"An invalid choice": 3},
        text="Text"
    )

    dialog = Dialog(
        dialog_id=0,
        nodes=[node]
    )

    with pytest.raises(RuntimeError) as e:
        node.get_option_text()  # Should throw error
        assert "No such node" in e.value  # Check that it's the expected error
