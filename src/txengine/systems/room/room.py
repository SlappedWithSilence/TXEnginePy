from .action import Action


class Room:
    """A room represents a scene in TXEngine. The user may interact with a number of functions inside any given room.

    A room's contents are defined by which Actions it contains. A room may contain any number of actions. Every room,
    by default, contains some pre-defined set of default actions.
    """

    def __init__(self, room_id: int, name: str, actions: list, on_first_enter_actions=None,
                 on_first_enter_text: str = None, ignore_default_actions: bool = False):
        super().__init__(name)
        self.id: int = room_id
        self.on_first_enter_actions: list = on_first_enter_actions or []
        self.actions: list[Action] = actions
        self.on_first_enter_text: str = on_first_enter_text
        self.ignore_default_actions: bool = ignore_default_actions

    def enter(self):
        pass

    def submit(self, user_input: int) -> [str, None]:

        if user_input > len(self.actions):
            return None

        self.actions[user_input].perform()

    @property
    def options(self) -> list[str]:
        return [action.menu_name for action in self.actions]

