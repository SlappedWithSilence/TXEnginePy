from abc import ABC


class Action(ABC):

    def __init__(self, menu_name: str,
                 properties: list[str],
                 hidden: bool,
                 reveal_index: int,
                 hide_after_use: bool,
                 requirements: list):

        self.menu_name: str = menu_name  # Text that appears in the room menu
        self.properties: list[str] = properties  # Configuration values
        self.hidden: bool = hidden  # If true, action is visible in room menu, if false it is hidden
        self.reveal_index: int = reveal_index  # If > -1, the action at the given index is set to hidden=false after use
        self.hide_after_use: bool = hide_after_use  # If true, self.hidden=true after use
        self.requirements: list = requirements  # All requirements must be met to execute action

    def perform(self):
        """Executes the logic associated with this action. Subclasses of Action must define this function."""
        pass
