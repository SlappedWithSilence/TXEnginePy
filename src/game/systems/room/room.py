import weakref

import game
import game.structures.enums as enums
import game.structures.state_device as state_device
import game.systems.action.actions as actions
import game.systems.room as room


class Room(state_device.StateDevice):

    def __init__(self, id: int, action_list: list[actions.Action], enter_text: str, first_enter_text: str = "", name: str = "Room"):
        super().__init__(input_type=enums.InputType.INT, name=name)

        self.actions: list[actions.Action] = action_list
        self.enter_text: str = enter_text  # Text that is printed each time room is entered
        self.first_enter_text: str = first_enter_text  # Text only printed the first time the user enters the room
        self.id: int = id
        self.domain_min = 0  # The domain min is always 0 for a room.

        # Register self as the owner of each Action
        for action in self.actions:
            action.room = weakref.proxy(self)

    @property
    def visible_actions(self) -> list[actions.Action]:
        """Returns a list containing only the actions that are visible in the room"""
        return [weakref.proxy(action) for action in self.actions if action.visible]

    @property
    def options(self) -> list[str]:
        """Returns a formatted string containing a numbered menu of actions"""
        return [opt.menu_name for opt in self.visible_actions]

    @property
    def components(self) -> dict[str, any]:
        # Update domain maximum in case an action was hidden or made visible
        self.domain_max = len(self.options) - 1

        return {"content": (self.first_enter_text + "\n" if room.room_manager.is_visited(self.id) else "") + self.enter_text,
                "options": self.options,
                }

    def _logic(self, user_input: any) -> None:

        # If the user selected and ExitAction, terminate the current room
        if type(self.visible_actions[user_input] == actions.ExitAction):
            game.state_device_controller.set_dead()

        # Execute selected option
        game.state_device_controller.add_state_device(self.visible_actions[user_input])  # Launch the selected Action as a StateDevice




