from abc import ABC
from typing import Union

from ..event.events import Event


class Action(ABC):

    def __init__(self, menu_name: str,
                 properties: list[str],
                 visible: bool,
                 reveal_index: int,
                 hide_after_use: bool,
                 requirements: list):
        self.menu_name: str = menu_name  # Text that appears in the room menu
        self.properties: list[str] = properties  # Configuration values
        self.visible: bool = visible  # If true, action is visible in room menu, if false it is hidden
        self.reveal_index: int = reveal_index  # If > -1, the action at the given index is set to hidden=false after use
        self.hide_after_use: bool = hide_after_use  # If true, self.hidden=true after use
        self.requirements: list = requirements  # All requirements must be met to execute action

    def perform(self) -> None:
        """Executes the logic associated with this action. Subclasses of Action must define this function."""
        pass


class ExitAction(Action):

    def __init__(self, menu_name: str, properties: list[str], visible: bool, reveal_index: int, hide_after_use: bool,
                 requirements: list, on_exit: Union[list[Event], None]):
        super().__init__(menu_name, properties, visible, reveal_index, hide_after_use, requirements)

        self.__on_exit: list[Event] = on_exit or []

    def perform(self) -> None:
        for event in self.__on_exit:
            event.perform()