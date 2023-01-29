from .action import Action
from ...structures.state_device import StateDevice
from ...ui.color import style


class Room (StateDevice):
    """A room represents a scene in TXEngine. The user may interact with a number of functions inside any given room.

    A room's contents are defined by which Actions it contains. A room may contain any number of actions. Every room,
    by default, contains some pre-defined set of default actions.
    """

    def __init__(self, room_id: int, name: str, actions: list, on_first_enter_actions=None,
                 on_first_enter_text: str = None, text: str = None, ignore_default_actions: bool = False):
        super().__init__()
        self.id: int = room_id  # Unique mapping ID
        self.on_first_enter_actions: list = on_first_enter_actions or []  # Actions that trigger only on first enter
        self.actions: list[Action] = actions  # Actions available for selections
        self.on_first_enter_text: str = on_first_enter_text or ""  # Text that is played only of first enter
        self.ignore_default_actions: bool = ignore_default_actions  # If true, do not show default actions
        self.text: str = text or ""

    def enter(self) -> None:
        """Enter a loop that only ends when the user selects an ExitAction"""
        pass

    @property
    def visible_actions(self) -> list[Action]:
        """Returns a list containing only the actions that are visible in the room"""
        return [action for action in self.actions if action.visible]

    @property
    def options(self) -> str:
        """Returns a formatted string containing a numbered menu of actions"""
        opt_names = [opt.menu_name for opt in self.visible_actions]
        base = ""

        for index, opt_name in enumerate(opt_names):
            index_box = f"[{index}]"
            base = base + style(index_box, "index") + " " + style(opt_name, "listed_option") + "\n"

        return base
