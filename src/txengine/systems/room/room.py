import weakref

from .action_device import ActionDevice, ExitAction
from ..managers.engine import Engine
from ...structures import enums
from ...structures.enums import InputType
from ...structures.state_device import StateDevice
from ..room import room_manager


class Room(StateDevice):
    """A room represents a scene in TXEngine. The user may interact with a number of functions inside any given room.

    A room's contents are defined by which Actions it contains. A room may contain any number of actions. Every room,
    by default, contains some pre-defined set of default actions.
    """

    def __init__(self, room_id: int, name: str, actions: list, owner: Engine, on_first_enter_actions=None,
                 on_first_enter_text: str = None, text: str = None, ignore_default_actions: bool = False):
        super().__init__(input_type=InputType.INT, input_range=enums.to_range(min_value=0))
        self.name = name
        self.id: int = room_id  # Unique mapping ID
        self.on_first_enter_actions: list = on_first_enter_actions or []  # Actions that trigger only on first enter
        self.actions: list[ActionDevice] = actions  # Actions available for selections
        self.on_first_enter_text: str = on_first_enter_text or ""  # Text that is played only of first enter
        self.ignore_default_actions: bool = ignore_default_actions  # If true, do not show default actions
        self.text: str = text or ""
        self.owner: Engine = owner
        self.domain_max = len(self.options)

    @property
    def visible_actions(self) -> list[ActionDevice]:
        """Returns a list containing only the actions that are visible in the room"""
        return [weakref.proxy(action) for action in self.actions if action.visible]

    @property
    def options(self) -> list[str]:
        """Returns a formatted string containing a numbered menu of actions"""
        return [opt.menu_name for opt in self.visible_actions]

    @property
    def components(self) -> dict[str, any]:
        return {"content": (self.on_first_enter_text + "\n" if room_manager.is_visited(self.id) else "") + self.text,
                "options": self.options,
                }

    def _logic(self, user_input: any) -> None:

        # Execute selected option

        self.owner.add_device(self.visible_actions[user_input])  # Launch the selected Action as a StateDevice

        # If the user selected and ExitAction, terminate the current room
        if type(self.visible_actions[user_input] == ExitAction):
            self.owner.set_dead()

        # Update domain maximum in case an action was hidden or made visible
        self.domain_max = len(self.options)
