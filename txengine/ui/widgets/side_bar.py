from typing import Optional

from rich.align import Align
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from textual import events
from textual.widget import Widget
from textual.widgets import ScrollView


class HistorySideBar(ScrollView):

    def on_mount(self, event: events.Mount) -> None:
        pass


class SummarySideBar(Widget):
    """Side bar for displaying critical info such as resource quantity, money, etc"""

    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.root_table: Table = None
        self.root_panel: Panel = None

        self.resource_bar_ids: dict = {}
        self.progress_handler: Progress = Progress()

        self.__init_table()

    #####################
    # Private Functions #
    #####################

    def __get_currency_panel(self):
        currency_table = Table()
        currency_table.add_column("Type")
        currency_table.add_column("Quantity")
        for currency in ["Money"]:  # TODO: Fetch correct list of currencies
            currency_table.add_row(currency, "15")  # TODO: Fetch correct currency values

        return Panel(Align.center(currency_table), title="Currency")

    def __init_table(self):
        """Logic for setting up the table"""
        self.root_table = Table()
        self.root_table.add_column("[bold][blue]Summary[/bold][/blue]")
        self.root_table.add_row(self.progress_handler)
        self.root_table.add_row(self.__get_currency_panel())

    def __update_resource_panel(self):
        # Update each progress bar
        for resource in self.resource_bar_ids:
            task_id = self.resource_bar_ids[resource]
            value = 50  # TODO: Fetch correct resource value
            self.progress_handler.update(task_id=task_id, completed=value)

    def __update_currency_panel(self):
        # TODO: Implement
        pass

    def __update(self):
        """Logic for updating contents of root panel"""
        self.__update_resource_panel()
        self.__update_currency_panel()

        # Finalize root panel
        self.root_panel = Align.center(Panel(self.root_table))
        self.refresh()

    ####################
    # Public Functions #
    ####################

    def register_resource(self, combat_resource_name: str):
        """Tell side-bar to track a given combat resource"""

        if True:  # TODO: Check if resource name is valid
            resource_total: int = 100  # TODO: Fetch up to date resource total
            self.resource_bar_ids[combat_resource_name] = self.progress_handler.add_task(
                f"[cyan]{combat_resource_name}",
                total=resource_total
            )

    # Textual Functions

    def render(self):
        """Render code"""
        self.__update()
        return self.root_panel
