from abc import ABC

from src.game.structures.state_device import StateDevice
from src.game.systems.requirement.requirements import RequirementsMixin


class Action(StateDevice, RequirementsMixin, ABC):
    """
    Base class for all actions.
    """

    def __init__(self, menu_name: str, activation_text, hidden: bool = False, reveal_other_action_index: int = -1,
                 hide_after_use: bool = False, *args):
        super().__init__(*args)

        self.menu_name: str = menu_name  # Name of the Action when viewed from a room
        self.activation_text: str = activation_text  # Text that is printed when the Action is run
        self.hidden: bool = hidden  # If True, not visible in the owning Room
        self.reveal_other_action_index: int = reveal_other_action_index  # If >= 0 set room.actions[idx].hidden to False
        self.hide_after_use: bool = hide_after_use  # If True, the action will set itself to hidden after being used
        self.room = None  # The Room that owns this action. Should ONLY be a weakref.proxy
