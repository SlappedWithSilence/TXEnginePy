class RoomManager:

    def __init__(self):
        self._current_room_index = 0
        self._visited_rooms = set()

    def is_visited(self, room_id: int) -> bool:
        return room_id in self._visited_rooms

    def visit(self, room_id: int) -> None:
        self._visited_rooms.add(room_id)

    @property
    def current_room(self) -> int:
        return self._current_room_index




# Define package-level globals
room_manager = RoomManager()
