import weakref

from ...structures.enums import InputType
from ...structures.state_device import StateDevice
from ..action.actions import Action, ExitAction


class Room(StateDevice):

    def __init__(self, id: int, actions: list[Action], enter_text: str, first_enter_text: str = "", name: str = "Room"):
        super().__init__(input_type=InputType.INT, name=name)

        self.actions: list[Action] = actions
        self.enter_text: str = enter_text  # Text that is printed each time room is entered
        self.first_enter_text: str = first_enter_text  # Text only printed the first time the user enters the room
        self.id: int = id

    @property
    def visible_actions(self) -> list[Action]:
        """Returns a list containing only the actions that are visible in the room"""
        return [weakref.proxy(action) for action in self.actions if action.visible]

    @property
    def options(self) -> list[str]:
        """Returns a formatted string containing a numbered menu of actions"""
        return [opt.menu_name for opt in self.visible_actions]

    @property
    def components(self) -> dict[str, any]:
        from . import room_manager
        return {"content": (self.first_enter_text + "\n" if room_manager.is_visited(self.id) else "") + self.enter_text,
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
