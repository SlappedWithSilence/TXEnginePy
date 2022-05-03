from typing import Optional

from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.pretty import Pretty
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget


class TriggerButton(Widget, can_focus=True):
    has_focus: Reactive[bool] = Reactive(False)
    mouse_over: Reactive[bool] = Reactive(False)
    style: Reactive[str] = Reactive("")
    height: Reactive[Optional[int]] = Reactive(None)

    def __init__(self, *,
                 name: Optional[str] = None,
                 height: Optional[int] = None,
                 text: str,
                 on_press: callable) -> None:
        super().__init__(name=name)
        self.height = height
        self.text = text
        self.trigger = on_press

    def render(self) -> RenderableType:
        return Panel(
            Align.center(
                Pretty(self.text, no_wrap=True, overflow="ellipsis"), vertical="middle"
            ),
            title=self.__class__.__name__,
            border_style="green" if self.mouse_over else "blue",
            box=box.HEAVY if self.has_focus else box.ROUNDED,
            style=self.style,
            height=self.height,
        )

    async def on_click(self, event: events.Click) -> None:
        self.trigger()

    async def on_focus(self, event: events.Focus) -> None:
        self.has_focus = True

    async def on_blur(self, event: events.Blur) -> None:
        self.has_focus = False

    async def on_enter(self, event: events.Enter) -> None:
        self.mouse_over = True

    async def on_leave(self, event: events.Leave) -> None:
        self.mouse_over = False
