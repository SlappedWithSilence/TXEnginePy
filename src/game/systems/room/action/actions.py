from abc import ABC
from enum import Enum

import game
import game.cache as cache
import game.systems.room as room
from game.structures.enums import InputType
from game.structures.state_device import FiniteStateDevice
import game.systems.event.events as events
import game.systems.requirement.requirements as requirements
from game.structures.messages import StringContent, ComponentFactory


class Action(FiniteStateDevice, requirements.RequirementsMixin, ABC):
    """
    Base class for all actions.
    """

    def __init__(self, menu_name: str, activation_text: str,
                 states: Enum, default_state, default_input_type: InputType,
                 visible: bool = True, reveal_other_action_index: int = -1,
                 hide_after_use: bool = False, requirement_list: list[requirements.Requirement] = None, *args,
                 **kwargs):
        super().__init__(default_input_type, states, default_state, *args, **kwargs)

        self._menu_name: str = menu_name  # Name of the Action when viewed from a room
        self.activation_text: str = activation_text  # Text that is printed when the Action is run
        self.visible: bool = visible  # If True, visible in the owning Room
        self.reveal_other_action_index: int = reveal_other_action_index  # If >= 0 set room.actions[idx].hidden to False
        self.hide_after_use: bool = hide_after_use  # If True, the action will set itself to hidden after being used
        self.room: room.Room = None  # The Room that owns this action. Should ONLY be a weakref.proxy
        self.requirements = requirement_list or []

    @property
    def menu_name(self) -> str:
        """
        Programmatically return menu name. Some subclasses of Action may need to dynamically adjust this property.
        """

        return self._menu_name


class ExitAction(Action):
    """
    An Action that signal to the state_device_controller that the containing Room StateDevice should be terminated
    """

    class States(Enum):
        DEFAULT = 0

    def __init__(self, target_room: int, menu_name: str = None, visible: bool = True,
                 reveal_other_action_index: int = -1, hide_after_use: bool = False, requirement_list: list = None,
                 on_exit: list[events.Event] = None):
        super().__init__(menu_name, "", ExitAction.States, ExitAction.States.DEFAULT, InputType.ANY,
                         visible, reveal_other_action_index, hide_after_use, requirement_list)

        # Set instance variables
        self.target_room = target_room
        self.__on_exit: list[events.Event] = on_exit or []

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.ANY)
        def logic(_: any) -> None:
            cache.get_cache()["player_location"] = self.target_room
            room.room_manager.visit_room(self.room.id)  # Inform the room manager that this room has been "visited"
            game.state_device_controller.set_dead()

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get([f"You moved to {room.room_manager.get_name(self.target_room)}"])

    @property
    def menu_name(self) -> str:
        """
        Dynamically return a menu name that retrieves the room_name of the target Room
        """
        return f"Move to {room.room_manager.get_name(self.target_room)}"


class ViewInventoryAction(Action):

    def __init__(self, menu_name: str, activation_text: str, *args, **kwargs):
        super().__init__(menu_name, activation_text, *args, **kwargs)

    @property
    def components(self) -> dict[str, any]:
        pass

    def _logic(self, user_input: any) -> None:
        pass
