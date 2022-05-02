from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer
from textual_inputs import IntegerInput

from ..widgets.game_text_output import GameTextOutput
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
        self.game_text_output = GameTextOutput(name="game_text_output")

    ####################
    # Helper Functions #
    ####################

    def __init_text_io(self):
        self.root_grid.add_column("center")
        self.root_grid.add_row("output")
        self.root_grid.add_row("input")
        self.root_grid.add_areas(input="center,input", output="center,output")
        self.root_grid.add_widget(self.game_text_output, "output")
        self.root_grid.add_widget(self.user_input, "input")

    #####################
    # Textual Functions #
    #####################

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

        self.summary_side_bar.layout_offset_x = -40

        await self.game_text_output.set_content("Some Text", self.name)
