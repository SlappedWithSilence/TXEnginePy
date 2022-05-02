from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer

from ..widgets.side_bar import SideBar


class Game(App):

    #################
    # Class Members #
    #################

    show_bar = Reactive(False)

    ######################
    # Built-in Functions #
    ######################

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.side_bar: SideBar = None

    #####################
    # Textual Functions #
    #####################

    # Watchers
    def watch_show_bar(self, show_bar: bool) -> None:
        """Called when show_bar changes."""
        self.side_bar.animate("layout_offset_x", 0 if show_bar else -40)

    # Actions
    def action_toggle_sidebar(self) -> None:
        """Called when user hits 'b' key."""
        self.show_bar = not self.show_bar

    # Event
    async def on_load(self) -> None:
        """Bind keys"""
        await self.bind("b", "toggle_sidebar", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

        """Initialize instance variables"""
        self.side_bar = SideBar()

        # TODO: Remove Debug
        self.side_bar.register_resource("Health")
        self.side_bar.register_resource("Mana")

    async def on_mount(self) -> None:
        # Set up footer
        footer = Footer()
        await self.view.dock(footer, edge="bottom")

        # Set up sidebar
        await self.view.dock(self.side_bar, edge="left", size=40, z=1)

        self.side_bar.layout_offset_x = -40

