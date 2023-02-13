from abc import ABC

import game
import game.cache as cache
import game.systems.room as room
import game.structures.enums as enums
import game.structures.state_device as state_device
import game.systems.event.events as events
import game.systems.requirement.requirements as requirements


class Action(state_device.StateDevice, requirements.RequirementsMixin, ABC):
    """
    Base class for all actions.
    """

    def __init__(self, menu_name: str, activation_text: str, visible: bool = True, reveal_other_action_index: int = -1,
                 hide_after_use: bool = False, requirement_list: list[requirements.Requirement] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.menu_name: str = menu_name  # Name of the Action when viewed from a room
        self.activation_text: str = activation_text  # Text that is printed when the Action is run
        self.visible: bool = visible  # If True, visible in the owning Room
        self.reveal_other_action_index: int = reveal_other_action_index  # If >= 0 set room.actions[idx].hidden to False
        self.hide_after_use: bool = hide_after_use  # If True, the action will set itself to hidden after being used
        self.room: room.Room = None  # The Room that owns this action. Should ONLY be a weakref.proxy
        self.requirements = requirement_list or []


class ExitAction(Action):

    def __init__(self, target_room: int, menu_name: str = None, visible: bool = True,
                 reveal_other_action_index: int = -1, hide_after_use: bool = False, requirement_list: list = None,
                 on_exit: list[events.Event] = None):
        super().__init__(input_type=enums.InputType.AFFIRMATIVE, menu_name=menu_name, activation_text="", visible=visible,
                         reveal_other_action_index=reveal_other_action_index, hide_after_use=hide_after_use,
                         requirement_list=requirement_list)

        # Set instance variables
        self.target_room = target_room
        self.input_type = enums.InputType.AFFIRMATIVE
        self.__on_exit: list[events.Event] = on_exit or []
        self.menu_name = self.menu_name or f"Go to LOOK UP ROOM NAME::{target_room}"

    # Override abstract methods
    def _logic(self, user_input: any) -> None:

        cache.get_cache()["player_location"] = self.target_room
        room.room_manager.visit_room(self.room.id)  # Inform the room manager that this room has been "visited"
        game.state_device_controller.set_dead()  # Set the action as dead

    @property
    def components(self) -> dict[str, any]:
        return {"content": f"Do you want to move to {self.target_room}"}


class TestAction(Action):

    def __init__(self, menu_name: str, activation_text, *args, **kwargs):
        super().__init__(menu_name, activation_text, *args, **kwargs)

    @property
    def components(self) -> dict[str, any]:
        return {"content": "Test"}

    def _logic(self, user_input: any) -> None:
        pass


if __name__ == "__main__":
    a = TestAction("Test", "Test", input_type=enums.InputType.NONE, name="TestAction", requirements=[])
    print(a.__dict__)
    print(a.is_requirements_fulfilled())
