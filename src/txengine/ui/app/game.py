import time

from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer
from textual_inputs import IntegerInput

from ..widgets.game_text_output import GameTextOutput, MenuElement
from ..widgets.side_bar import SummarySideBar, HistorySideBar


class Game(App):
    #################
    # Class Members #
    #################

    # Stores
    text_history = []

    # Reactives
    show_bar = Reactive(False)

    ######################
    # Built-in Functions #
    ######################

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Metadata
        self.root_grid = None
        self.name = "TXEngine Default Name"

        # Offscreen elements
        self.summary_side_bar: SummarySideBar = None
        self.history_side_bar: HistorySideBar = None

        # Text IO elements
        self.user_input = IntegerInput(name="user_input", title="Input")
        self.game_dialog_pane = GameTextOutput(name="game_dialog_pane")
        self.game_menu_pane = GameTextOutput(name="game_menu_pane")

    ####################
    # Helper Functions #
    ####################

    def __init_text_io(self):
        self.root_grid.add_column("center")
        self.root_grid.add_row("dialog_pane")
        self.root_grid.add_row("menu_pane")
        self.root_grid.add_row("input_box")
        self.root_grid.add_areas(input="center,input_box",
                                 dialog_pane="center,dialog_pane",
                                 menu_pane="center,menu_pane"
                                 )
        self.root_grid.add_widget(self.game_dialog_pane, "dialog_pane")
        self.root_grid.add_widget(self.game_menu_pane, "menu_pane")
        self.root_grid.add_widget(self.user_input, "input")

    #####################
    # Textual Functions #
    #####################

    # Handlers
    def handle_game_text_change(self):
        """Add the on-screen text to the history"""
        prefix = self.game_dialog_pane.current_source or self.name
        self.text_history.append(f"[{prefix}]{self.game_dialog_pane.current_text}")

    # Watchers
    def watch_show_bar(self, show_bar: bool) -> None:
        """Called when show_bar changes."""
        self.summary_side_bar.animate("layout_offset_x", 0 if show_bar else -40)

    # Actions
    def action_toggle_sidebar(self) -> None:
        """Called when user hits 'b' key."""
        self.show_bar = not self.show_bar

    # Event
    async def on_load(self) -> None:
        """Bind keys"""
        await self.bind("b", "toggle_sidebar", "Toggle summary")
        await self.bind("q", "quit", "Quit")
        await self.bind("s", "save", "Save")

        """Initialize instance variables"""
        self.summary_side_bar = SummarySideBar()

        # TODO: Remove Debug
        self.summary_side_bar.register_resource("Health")
        self.summary_side_bar.register_resource("Mana")

    async def on_mount(self) -> None:
        # Set up footer
        footer = Footer()
        await self.view.dock(footer, edge="bottom")

        # Set up text IO
        self.root_grid = await self.view.dock_grid(edge="top", name="root_grid", gutter=0)
        self.__init_text_io()

        # Set up sidebar
        await self.view.dock(self.summary_side_bar, edge="left", size=40, z=1)

        await self.game_dialog_pane.set_content(
            MenuElement(["an option", "another option"], header="[blue][italic]Some Options[/italic][/blue]"),
            self.name
        )

        self.summary_side_bar.layout_offset_x = -40
