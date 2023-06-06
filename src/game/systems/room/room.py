"""
Contains the main Room object
"""
import weakref
from enum import Enum

import game
from game.cache import from_cache, cached
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.loadable_factory import LoadableFactory
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice

import game.systems.room as room
import game.systems.room.action.actions as actions

from loguru import logger


class Room(LoadableMixin, FiniteStateDevice):
    """
    A StateDevice that simulates a user being inside a "scene" or "room". Rooms act as a container for Actions, of which
    a Room may have many.
    """

    class States(Enum):
        DEFAULT = 0
        DISPLAY_OPTIONS = 1
        REQ_MET = 2
        REQ_NOT_MET = 3
        LEAVE_ROOM = 4
        TERMINATE = -1

    def __init__(self, rid: int, action_list: list[actions.Action], enter_text: str, first_enter_text: str = "",
                 name: str = "Room"):
        super().__init__(InputType.INT, self.States, self.States.DEFAULT)

        self.actions: list[actions.Action] = action_list
        self.enter_text: str = enter_text  # Text that is printed each time room is entered
        self.first_enter_text: str = first_enter_text  # Text only printed the first time the user enters the room
        self.id: int = rid
        self._action_index: int = None
        self.name = name

        # Register self as the owner of each Action
        for action in self.actions:
            action.room = weakref.proxy(self)

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            self.set_state(self.States.DISPLAY_OPTIONS)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.DISPLAY_OPTIONS, InputType.INT, 0,
                                       lambda: len(self.options) - 1)
        def logic(user_input: int) -> None:
            self._action_index = user_input

            if not self.visible_actions[user_input].is_requirements_fulfilled(from_cache('player')):
                logger.warning("Requirements not met!")
                self.set_state(self.States.REQ_NOT_MET)
                return

            self.set_state(self.States.REQ_MET)

        @FiniteStateDevice.state_content(self, self.States.DISPLAY_OPTIONS)
        def content():
            return ComponentFactory.get(
                [(self.first_enter_text + "\n" if room.room_manager.is_visited(self.id) else "") + self.enter_text],
                self.options
            )

        @FiniteStateDevice.state_logic(self, self.States.REQ_MET, InputType.SILENT)
        def logic(_) -> None:
            game.state_device_controller.add_state_device(self.visible_actions[self._action_index])

            if isinstance(self.visible_actions[self._action_index], actions.ExitAction):
                self.set_state(self.States.LEAVE_ROOM)
            else:
                self.set_state(self.States.DISPLAY_OPTIONS)

        @FiniteStateDevice.state_content(self, self.States.REQ_MET)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.REQ_NOT_MET, InputType.ANY)
        def logic(_) -> None:
            self.set_state(self.States.DISPLAY_OPTIONS)

        @FiniteStateDevice.state_content(self, self.States.REQ_NOT_MET)
        def content():
            return ComponentFactory.get(
                ["You can't do that!"],
                self.visible_actions[self._action_index].get_requirements_as_options()
            )

        @FiniteStateDevice.state_logic(self, self.States.LEAVE_ROOM, InputType.ANY)
        def logic(_) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.LEAVE_ROOM)
        def content():
            return ComponentFactory.get([f"You leave {self.name}"])

    @property
    def visible_actions(self) -> list[actions.Action]:
        """Returns a list containing only the actions that are visible in the room"""
        return [weakref.proxy(action) for action in self.actions if action.visible]

    @property
    def options(self) -> list[list[str | StringContent]]:
        """Returns a formatted string containing a numbered menu of actions"""
        return [[opt.menu_name] for opt in self.visible_actions]

    @staticmethod
    @cached(LoadableMixin.CACHE_PATH.format("Room"))
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a Room object from a JSON blob.

        Required JSON fields:
        - name: str
        - id: int
        - enter_text: str
        - first_enter_text: str
        - actions: list[Action]

        Optional JSON fields:
        - None
        """

        required_fields: list[tuple[str, type]] = [
            ("name", str), ("id", int), ("enter_text", str), ("first_enter_text", str),
            ("actions", list),

        ]

        LoadableFactory.validate_fields(required_fields, json)

        if json["class"] != "Room":
            raise ValueError(f"Room loader expected class field value of 'Room', got {json['class']} instead!")

        _actions = []
        for raw_action in json['actions']:
            action = LoadableFactory.get(raw_action)
            if not isinstance(action, actions.Action):
                raise TypeError(f"Expected object of type Action, got {type(action)} instead!")

            _actions.append(action)

        return Room(
            json['id'],
            _actions,
            json['enter_text'],
            json['first_enter_text'],
            json['name']
        )
