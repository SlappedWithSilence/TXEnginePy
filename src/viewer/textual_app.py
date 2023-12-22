from dataclasses import dataclass

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Input, Tabs, Tab, TabbedContent, TabPane, Label, Button


# Global helper functions
def formatting_to_tags(tags: list[str], opening_tag: bool = None, closing_tag: bool = None) -> str:
    """Helper function for format_string"""
    buf = ""
    if opening_tag:
        for tag in tags:
            buf = buf + f"[{tag}]"

    elif closing_tag:
        for tag in tags:
            buf = buf + f"[/{tag}]"

    return buf


def format_string(content: str, tags: list[str]) -> str:
    """A helper function that wraps a content str in a set of Rich tags"""
    return formatting_to_tags(tags, opening_tag=True) + content + formatting_to_tags(tags, closing_tag=True)


def parse_content(content: list) -> str:
    """
    Parse the elements inside the 'content' JSON field of a frame. Translate into a Rich-readable string.
    """
    buf = ""
    for element in content:
        if type(element) == str:
            buf = buf + element
        elif type(element) == dict:
            buf = buf + \
                  formatting_to_tags(element['formatting'], opening_tag=True) + \
                  element['value'] + \
                  formatting_to_tags(element['formatting'], closing_tag=True)
    return buf


def input_type_to_regex(input_type: str, input_range: dict = None) -> str | None:
    if type(input_type) != str:
        raise TypeError()

    if input_range is not None and type(input_range) != dict:
        raise TypeError()

    match input_type:
        case "int":
            return r"[0-9]*"

        case "affirmative":
            return r"[y,n,Y,N]"

        case "str":
            return None

        case "any":
            return None

        case _:
            raise RuntimeError("Unknown Input Type!")


# Global helper classes
@dataclass
class HistoryEntry:
    """
    A simple dataclass that holds a record for a previous game frame and the user's input
    """

    content: dict
    user_input: int | str


class OptionsTableFactory:
    """
    A factory class that reads a frame_type context and returns a pre-configured DataTable to display
    a list of choices to the user
    """
    IDX_COL_NAME = "Selection"
    CHOICE_COL_NAME = "Choice"

    context_map: dict[str, dict[str, any]] = {
        "Room": {
            "columns": [IDX_COL_NAME, "Action"]
        },
        "default": {
            "columns": [IDX_COL_NAME, CHOICE_COL_NAME]
        }
    }

    @classmethod
    def get(cls, options: list[list[str | dict]], context: str) -> DataTable:
        if type(options) != dict:
            raise TypeError()

        if type(context) != str:
            raise TypeError()

        dt = DataTable()

        # Configure column names
        if context in cls.context_map:
            dt.add_columns(*cls.context_map[context]["columns"])
        else:
            dt.add_columns(*cls.context_map["default"]["columns"])

        # Add row data
        dt.add_rows([parse_content(opt) for opt in options])

        return dt


class OptionsTable(Static):
    """
    A pre-configured table widget that cleanly displays the available options to the user
    """

    def __init__(self, options_data: list[list[str | dict]], frame_type: str, **kwargs):
        super().__init__(**kwargs)

        self._options_data = options_data
        self._frame_type = frame_type

    def compose(self) -> ComposeResult:
        """
        Create the child widgets of an OptionsTable.
        """
        yield OptionsTableFactory.get(self._options_data, self._frame_type)


class HistoryWidget(Static):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._frame_history = self.app.frame_history
        self._frame_index = self.app.current_history_index

    def compose(self) -> ComposeResult:
        yield Label("Some previous screen")
        yield Button("Back")
        yield Button("Forward")


class MainScreen(Static):
    """
    The main screen content for the app. Handles app switching and populating with elements
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="game_screen"):
            with TabPane("Game", id="game_screen"):
                yield Label("Game Content Goes Here", id="game_screen_content")
            with TabPane("History", id="history_screen"):
                yield HistoryWidget()


class TextualViewer(App):
    BINDINGS = [
        ("l", "show_tab('game_screen')", "Game"),
        ("j", "show_tab('history_screen')", "History")
    ]

    def __init__(self):
        super().__init__()

        self.frame_history: list[HistoryEntry] = []
        self.current_history_index: int | None = None

    @property
    def is_viewing_history(self) -> bool:
        return self.current_history_index is not None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(name="TXEngine")
        yield MainScreen(name="main_screen")
        yield Input(name="primary_user_input")
        yield Footer()

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(MainScreen).get_child_by_type(TabbedContent).active = tab


if __name__ == "__main__":
    app = TextualViewer()
    app.run()