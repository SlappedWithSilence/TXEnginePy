from typing import Union

from .room import Room
from ..player import player

from rich import print


class RoomManager:
    """Manages the information related to rooms and dispatches the player into them."""

    visited_rooms: set[int]
    rooms = dict[int, Room]

    def __init__(self, visited_rooms: Union[set[int], None] = None,
                 rooms: Union[dict[int, Room], None] = None) -> None:
        self.visited_rooms = visited_rooms or set()
        self.rooms = rooms or {}

def start_room_loop() -> RoomManager:
    """Starts the main game loop."""

    while True:
        if player.room_index in self.rooms:

            # Handle first-entry
            if player.room_index not in self.visited_rooms:
                print(self.rooms[player.room_index].on_first_enter_text)
                self.visited_rooms.add(player.room_index)

            # Start inner room-loop
            self.rooms[player.room_index].enter()

        else:
            raise ValueError(f"Player room index {player.room_index} is out bounds!")
