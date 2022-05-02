from typing import Union

from rich.console import RenderableType
from rich.panel import Panel
from textual.message import Message
from textual.widget import Widget


class GameTextChange(Message, bubble=True):
    _handler: str = "handle_game_text_change"


class GameTextOutput(Widget):
    current_source: str = None
    current_text: str = None

    async def set_content(self, text: str, source: Union[str, None]):
        self.current_text = text
        self.current_source = source
        await self.emit(GameTextChange(self))

    def render(self) -> RenderableType:
        return Panel(self.current_text or "", title=self.current_source)
