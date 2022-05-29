from typing import Union

from src.txengine.systems.room.room import Room
from src.txengine.systems.player import player


class RoomManager:
    """Manages the information related to rooms and dispatches the player into them."""

    visited_rooms: list[int]
    rooms = dict[int, Room]

    def __init__(self, visited_rooms: Union[list[int], None] = None,
                 rooms: Union[dict[int, Room], None] = None) -> None:
        self.visited_rooms = visited_rooms or []
        self.rooms = rooms or {}

    def start_room_loop(self) -> None:
        """Starts the main game loop."""

        while True:
            if player.room_index in self.rooms:
                self.rooms[player.room_index].enter()

            else:
                raise ValueError(f"Player room index {player.room_index} is out bounds!")
