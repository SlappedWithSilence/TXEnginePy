from abc import ABC
from typing import Union

from rich.console import RenderableType
from rich.panel import Panel
from textual.message import Message
from textual.widget import Widget

from ..color.colors import c_form

class GameTextElement(ABC):

    def __init__(self, source: str = None):
        self.source: Union[str, None] = source

    def unpack(self) -> str:
        return ""


class MenuElement(GameTextElement):

    def __init__(self,  opts: list[str], source: str = None, header: str = None):
        super().__init__(source)

        # Check for valid opts
        if len(opts) < 1:
            raise ValueError("MenuElement.opts must have length > 1!")

        self.opts: list[str] = opts  # The set of options the player may choose from
        self.header: [str, None] = header  # The text that may appear over the options

    def unpack(self) -> str:

        base = ""

        if self.header:
            base = self.header + "\n"

        for i in range(len(self.opts)):
            opt = c_form(f"[{i}]", "menu_opt_number") + f": " + c_form(self.opts[i], "menu_opt_text")
            base = base + opt + "\n"

        return base


class GameTextChange(Message, bubble=True):
    _handler: str = "handle_game_text_change"


class GameTextOutput(Widget):
    current_source: str = None
    current_text: str = None

    async def set_content(self, content: Union[str, GameTextElement], source: Union[str, None]):

        if self.current_text and self.current_text != "":
            await self.emit(GameTextChange(self))

        if type(content) == str:
            self.current_text = content
        elif isinstance(content, GameTextElement):
            self.current_text = content.unpack()

        self.current_source = source




    def render(self) -> RenderableType:
        return Panel(self.current_text or "", title=self.current_source)
