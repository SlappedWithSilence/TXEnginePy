import requests
from rich import print
from textual.app import App, ComposeResult
from textual.reactive import Reactive
from textual.widgets import Header, Footer, Static


def formatting_to_tags(tags: list[str], opening_tag: bool = None, closing_tag: bool = None) -> str:
    buf = ""
    if opening_tag:
        for tag in tags:
            buf = buf + f"[{tag}]"

    elif closing_tag:
        for tag in tags:
            buf = buf + f"[/{tag}]"

    return buf


def parse_content(content: list) -> str:
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


class Viewer:
    """
    A basic class that visualizes the TXEngine API
    """

    def __init__(self):
        u = input("Enter the IP for the TXEngine server: ")
        self.ip = 'http://' + (u if u != "" else "localhost:8000")

    def display(self, value: dict):
        """
        Primitively print GET results
        """

        def entity_to_str(entity_dict: dict[str, any]) -> str:
            return f"{entity_dict['name']}\n{entity_dict['primary_resource_name']}: [{entity_dict['primary_resource_val']}/{entity_dict['primary_resource_max']}]"

        print(parse_content(value["components"]["content"]))

        if "enemies" in value["components"]:
            print("ENEMIES")
            for enemy in value["components"]["enemies"]:
                print(entity_to_str(enemy))

        if "allies" in value["components"]:
            print("ALLIES")
            for ally in value["components"]["allies"]:
                print(entity_to_str(ally))

        if "options" in value["components"] and type(value["components"]["options"]) == list:
            for idx, opt in enumerate(value["components"]["options"]):
                print(f"[{idx}] {parse_content(opt)}")

        input_type = value["input_type"][0]
        input_range = value["input_range"]

        if input_type == "int":
            print(f"Enter a number between ({input_range['min']} and {input_range['max']}):")

        elif input_type == "none":
            print(f"Press any key:")

        elif input_type == "str":
            print("Enter a string: ")

        elif input_type == "affirmative":
            print("Enter y, n, yes, or no:")
        elif input_type == "any":
            print("Press any key...")


class TextualViewer(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    """
    viewer = Viewer()

    while True:
        results = requests.get(viewer.ip, verify=False)
        viewer.display(results.json())
        user_input = input()

        r = requests.put(viewer.ip, params={"user_input": user_input}, verify=False)
    """

    viewer = TextualViewer()
    viewer.run()
