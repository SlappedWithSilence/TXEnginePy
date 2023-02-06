import weakref
from abc import ABC
from typing import Union, Any

from ..event.events import Event
from ...structures.enums import InputType
from ...structures.state_device import StateDevice
from ..room import room_manager


class ActionDevice(StateDevice, ABC):

    def __init__(self, menu_name: str, visible: bool, reveal_index: int, hide_after_use: bool,
                 requirements: list, owner: Any = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_name: str = menu_name  # Text that appears in the room menu
        self.visible: bool = visible  # If true, action is visible in room menu, if false it is hidden
        self.reveal_index: int = reveal_index  # If > -1, the action at the given index is set to hidden=false after use
        self.hide_after_use: bool = hide_after_use  # If true, self.hidden=true after use
        self.requirements: list = requirements  # All requirements must be met to execute action
        self.owner = weakref.proxy(owner)  # This is actually always a Room


class ExitAction(ActionDevice):

    def __init__(self, menu_name: str, target_room: int, visible: bool, reveal_index: int, hide_after_use: bool,
                 requirements: list, on_exit: Union[list[Event], None]):
        super().__init__(menu_name, visible, reveal_index, hide_after_use, requirements)

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
