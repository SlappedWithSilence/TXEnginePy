import weakref
from abc import ABC
from enum import Enum

import game
import game.cache as cache
import game.systems.room as room
import game.systems.event.use_item_event as uie
from game.structures.enums import InputType
from game.structures.state_device import FiniteStateDevice
import game.systems.event.events as events
import game.systems.requirement.requirements as requirements
from game.structures.messages import StringContent, ComponentFactory
from game.systems import entity

from loguru import logger


class Action(FiniteStateDevice, requirements.RequirementsMixin, ABC):
    """
    Base class for all actions.
    """

    def __init__(self, menu_name: str, activation_text: str,
                 states: Enum, default_state, default_input_type: InputType,
                 visible: bool = True, reveal_other_action_index: int = -1,
                 hide_after_use: bool = False, requirement_list: list[requirements.Requirement] = None,
                 persistent: bool = False, *args, **kwargs):
        super().__init__(default_input_type, states, default_state, *args, **kwargs)

        self._menu_name: str = menu_name  # Name of the Action when viewed from a room
        self.activation_text: str = activation_text  # Text that is printed when the Action is run
        self.visible: bool = visible  # If True, visible in the owning Room
        self.reveal_other_action_index: int = reveal_other_action_index  # If >= 0 set room.actions[idx].hidden to False
        self.hide_after_use: bool = hide_after_use  # If True, the action will set itself to hidden after being used
        self.room: room.Room = None  # The Room that owns this action. Should ONLY be a weakref.proxy
        self.requirements: list = requirement_list or []
        self.persistent: bool = persistent

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
    class States(Enum):
        DEFAULT = 0
        DISPLAY_INVENTORY = 1
        INSPECT_STACK = 2
        DROP_STACK = 3
        CONFIRM_DROP_STACK = 4
        USE_ITEM = 5
        DESC_ITEM = 6
        EQUIP_ITEM = 7
        EMPTY = 8,
        TERMINATE = -1

    stack_inspect_options = {"Inspect": States.DESC_ITEM,
                             "Use": States.USE_ITEM,
                             "Equip": States.EQUIP_ITEM,
                             "Drop": States.CONFIRM_DROP_STACK}

    @classmethod
    def get_stack_inspection_options(cls) -> list[list[str]]:
        return [[opt] for opt in cls.stack_inspect_options.keys()]

    def __init__(self, *args, **kwargs):
        super().__init__("View inventory", "",
                         ViewInventoryAction.States, ViewInventoryAction.States.DEFAULT, InputType.SILENT,
                         *args, **kwargs)

        self.player_ref: entity.entities.Player = weakref.proxy(cache.get_cache()["player"])
        self.stack_index: int = None

        # DEFAULT

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

            if self.player_ref.inventory.size == 0:
                self.set_state(self.States.EMPTY)
            else:
                self.set_state(self.States.DISPLAY_INVENTORY)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get([""])

        # EMPTY

        @FiniteStateDevice.state_logic(self, self.States.EMPTY, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.EMPTY)
        def logic() -> dict:
            return ComponentFactory.get(["Your inventory is empty"])

        # DISPLAY_INVENTORY

        @FiniteStateDevice.state_logic(self, self.States.DISPLAY_INVENTORY, InputType.INT, -1,
                                       lambda: self.player_ref.inventory.size - 1)
        def logic(user_input: int) -> None:
            if user_input == -1:
                self.set_state(self.States.TERMINATE)
            else:
                self.stack_index = user_input
                self.set_state(self.States.INSPECT_STACK)

        @FiniteStateDevice.state_content(self, self.States.DISPLAY_INVENTORY)
        def content() -> dict:
            return ComponentFactory.get(["What stack would you like to inspect?"],
                                        self.player_ref.inventory.to_options())

        # INSPECT STACK
        @FiniteStateDevice.state_logic(self, self.States.INSPECT_STACK, InputType.INT, -1,
                                       len(self.stack_inspect_options) - 1)
        def logic(user_input: int) -> None:
            if user_input == -1:
                self.set_state(self.States.DISPLAY_INVENTORY)
            else:
                selected_option = list(self.stack_inspect_options.keys())[user_input]
                self.set_state(self.stack_inspect_options[selected_option])

        @FiniteStateDevice.state_content(self, self.States.INSPECT_STACK)
        def content() -> dict:
            c = ["What would you like to do with ",
                 StringContent(value=f"{self.player_ref.inventory.items[self.stack_index].ref.name}",
                               formatting="item_name"),
                 "?"
                 ]
            return ComponentFactory.get(c, self.get_stack_inspection_options())

        # CONFIRM_DROP_STACK

        @FiniteStateDevice.state_logic(self, self.States.CONFIRM_DROP_STACK, InputType.AFFIRMATIVE)
        def logic(user_input: bool) -> None:
            if user_input:
                self.set_state(self.States.DROP_STACK)
            else:
                self.set_state(self.States.INSPECT_STACK)

        @FiniteStateDevice.state_content(self, self.States.CONFIRM_DROP_STACK)
        def content() -> dict:
            stack = self.player_ref.inventory.items[self.stack_index]
            return ComponentFactory.get(
                [
                    "Are you sure you want to drop ",
                    StringContent(value=stack.ref.name, formatting="item_name"),
                    " ",
                    StringContent(value=f"{stack.quantity}x", formatting="item_quantity"),
                    "?"
                ]
            )

        # DROP_STACK

        @FiniteStateDevice.state_logic(self, self.States.DROP_STACK, InputType.ANY)
        def logic(_: any) -> None:
            self.player_ref.inventory.drop_stack(self.stack_index)
            self.set_state(self.States.DISPLAY_INVENTORY)

        @FiniteStateDevice.state_content(self, self.States.DROP_STACK)
        def content() -> dict:
            stack = self.player_ref.inventory.items[self.stack_index]
            return ComponentFactory.get(
                [
                    "You dropped ",
                    StringContent(value=f"{stack.quantity}x", formatting="item_quantity"),
                    " ",
                    StringContent(value=stack.ref.name, formatting="item_name"),
                    "."
                ]
            )

        # DESC_ITEM

        @FiniteStateDevice.state_logic(self, self.States.DESC_ITEM, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.INSPECT_STACK)

        @FiniteStateDevice.state_content(self, self.States.DESC_ITEM)
        def content() -> dict:
            return ComponentFactory.get([self.player_ref.inventory.items[self.stack_index].ref.description])

        # USE_ITEM

        @FiniteStateDevice.state_logic(self, self.States.USE_ITEM, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.add_state_device(uie.UseItemEvent(self.stack_index))
            self.set_state(self.States.INSPECT_STACK)

        @FiniteStateDevice.state_content(self, self.States.USE_ITEM)
        def content() -> dict:
            return ComponentFactory.get()

        # TERMINATE

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.set_dead()

        @FiniteStateDevice.state_content(self, self.States.TERMINATE)
        def content() -> dict:
            return ComponentFactory.get([""])
