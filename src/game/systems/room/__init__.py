import weakref

import game.systems.room.room as room
import game.systems.action.actions as actions
import game.structures.manager as manager

from loguru import logger


class RoomManager(manager.Manager):

    def __init__(self):
        super().__init__()

        logger.info("RoomManager::init")
        self.rooms: dict[int, room.Room] = {}
        self.visited_rooms: set[int] = set()
        self.load()
        logger.info("RoomManager::init.done")

    def register_room(self, room_object: room.Room, room_id_override: int = None) -> None:
        """
        Register a Room object with the RoomManager

        Args:
            room_object (int): The room to register
            room_id_override (int): An optional value that overrides the room_object's ID

        Returns: None
        """
        if room_object.id in self.rooms or room_id_override in self.rooms:
            raise ValueError(f"Cannot register duplicate room_id for room:{room_object.id}!")

        self.rooms[room_id_override or room_object.id] = room_object

    def get_room(self, room_id: int) -> room.Room:
        """
        Return a weak reference to the desired room.

        Args:
            room_id (int): The ID of the room the retrieve

        Returns: A weakref.proxy of the desired Room
        """

        if room_id not in self.rooms:
            raise ValueError(f"Cannot retrieve Room:{room_id}! No such Room exists!")

        return weakref.proxy(self.rooms[room_id])

    def visit_room(self, r: int | room.Room) -> None:
        """
        Sets a room as 'visited' by the RoomManager

        Args:
            r (int | Room): The room or room id to add.

        Returns: None
        """

        if type(r) == int:
            self.visited_rooms.add(r)
        elif type(r) == room.Room:
            self.visited_rooms.add(r.id)
        else:
            raise TypeError(f"Expected type int or Room! Got {type(r)} instead.")

    def is_visited(self, room_id: int) -> bool:
        """
        Returns True if the room_id has been visited before
        """

        return room_id in self.visited_rooms

    def load(self) -> None:

        exit_r_1 = actions.ExitAction(1)
        exit_r_0 = actions.ExitAction(0)

        r_0 = room.Room(action_list=[exit_r_1], enter_text="A debug room", id=0)
        r_1 = room.Room(action_list=[exit_r_0], enter_text="Another debug room", id=1)
        self.register_room(r_0)
        self.register_room(r_1)

    def save(self) -> None:
        pass


room_manager = RoomManager()
