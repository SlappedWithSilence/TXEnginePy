import copy
import dataclasses
from abc import ABC

import game
from game.systems.event import Event
from game.systems.requirement.requirements import RequirementsMixin


@dataclasses.dataclass
class DialogNodeBase(ABC):
    node_id: int  # Unique ID for the node. Every node must be unique, even when considered between dialogs.
    options: dict[str, dict[str, any]]
    text: str
    visited: bool = False
    allow_multiple_visits: bool = True
    multiple_event_triggers: bool = False  # If False, events will only trigger when visited==False
    persistent: bool = False  # If True, properties will be persisted in storage between sessions

    def get_option_text(self) -> list[str]:
        return [s for s in self.options.keys()]

    def get_next_node(self, option: str) -> int | None:
        """
        Get the next node to transition to after the current node is completed.
        """
        if option not in self.options.keys():
            raise ValueError(f"No such option: {option}")

        if "next node" not in self.options[option]:
            raise KeyError(f"Unable to find required key `next_node` for option {option}")

        return self.options[option]["next_node"]


class DialogNode(RequirementsMixin, DialogNodeBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.persistent:
            # Handle fetching properties from storage
            pass

    def should_trigger_events(self) -> None:
        """
        Determine if events should be triggered.
        """

        if not self.multiple_event_triggers and self.visited:
            return False

        return True

    def get_events(self) -> list[Event]:
        return [copy.deepcopy(e) for e in self.events]

    def trigger_events(self) -> None:
        """
        Run a deep copy of each event
        """

        for event in self.get_events():
            game.state_device_controller.add_state_device(event)


class Dialog:

    def __init__(self, nodes: list[DialogNode]):
        if len(nodes) < 1:
            raise ValueError("Unable to instantiate Dialog Object with zero nodes!")
