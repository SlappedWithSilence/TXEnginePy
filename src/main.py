from txengine.systems.room import room_manager
from txengine.systems.room.room import Room
from txengine.ui.color import init_default_tag_map
from txengine.cache import config


def init_debug() -> None:
    """Perform pre-game debugging functions"""
    acs = []
    r = Room(0, "The Alley", acs, text="You enter a spooky alleyway.")
    room_manager.rooms[0] = r


def init() -> None:
    """Initialize various engine elements"""
    init_default_tag_map()


if __name__ == "__main__":

    init()

    if config["debug"]:
        init_debug()

    room_manager.start_room_loop()
