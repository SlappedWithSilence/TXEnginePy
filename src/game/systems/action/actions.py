from abc import ABC

from src.game.structures.enums import InputType
from src.game.structures.state_device import StateDevice
from src.game.systems.event.events import Event
from src.game.systems.requirement.requirements import RequirementsMixin, Requirement


class Action(StateDevice, RequirementsMixin, ABC):
    """
    Base class for all actions.
    """

    def __init__(self, menu_name: str, activation_text, visible: bool = True, reveal_other_action_index: int = -1,
                 hide_after_use: bool = False, requirements: list[Requirement] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.menu_name: str = menu_name  # Name of the Action when viewed from a room
        self.activation_text: str = activation_text  # Text that is printed when the Action is run
        self.visible: bool = visible  # If True, visible in the owning Room
        self.reveal_other_action_index: int = reveal_other_action_index  # If >= 0 set room.actions[idx].hidden to False
        self.hide_after_use: bool = hide_after_use  # If True, the action will set itself to hidden after being used
        self.room = None  # The Room that owns this action. Should ONLY be a weakref.proxy
        self.requirements = requirements or []


class ExitAction(Action):

    def __init__(self, menu_name: str, target_room: int, visible: bool, reveal_other_action_index: int, hide_after_use: bool,
                 requirements: list, on_exit: list[Event] = None):
        super().__init__(menu_name=menu_name, activation_text="", visible=visible,
                         reveal_other_action_index=reveal_other_action_index, hide_after_use=hide_after_use,
                         requirements=requirements)

        # Set instance variables
        self.target_room = target_room
        self.input_type = InputType.AFFIRMATIVE
        self.__on_exit: list[Event] = on_exit or []

    # Override abstract methods
    def _logic(self, user_input: any) -> None:
        room_manager.visit(self.owner.id)  # Inform the room manager that this room has now been effectively "visited".
        self.owner.owner.set_dead()  # Set the action as dead

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
    a = TestAction("Test", "Test", input_type=InputType.NONE, name="TestAction", requirements=[])
    print(a.__dict__)
    print(a.is_requirements_fulfilled())
