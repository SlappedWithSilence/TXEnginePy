from typing import Union

from ..stats.stats import Stat


class Player:
    name: str
    stats: dict[str, Stat]
    skills: dict[str, any]  # TODO: Update typing after skills class is created
    room_index: int

    def __init__(self, stats: dict[str, Stat],
                 name: str = "Player",
                 room_index: int = 0
                 ) -> None:

        self.name: str = name
        self.room_index: int = room_index
        self.stats: dict[str, Stat] = stats


player = Player(stats={})
