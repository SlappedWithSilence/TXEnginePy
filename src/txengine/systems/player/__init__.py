from typing import Union

from src.txengine.systems.stats.stats import Stat
from src.txengine.systems.player.resource import Stat


class Player:
    name: str
    resources: dict[str, Stat]
    room_index: int

    def __init__(self, name: str = "Player",
                 resources: Union[dict[str, Stat], None] = None,
                 room_index: int = 0
                 ) -> None:

        self.name = name
        self.room_index = room_index

        if not resources:
            self.resources = {}
        else:
            self.resources = resources


player = Player()