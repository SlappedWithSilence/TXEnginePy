from txengine.systems.room import room_manager
from txengine.systems.room.room import Room
from txengine.ui.color import init_default_tag_map
from txengine.cache import config

from fastapi import FastAPI


# Define constants
app_server = FastAPI()


# Define helper functions
def init_debug() -> None:
    """Perform pre-game debugging functions"""


def init() -> None:
    """Initialize various engine elements"""


# Define FastAPI functions
@app_server.get("/")
async def root():
    return {"message": "Hello World"}
