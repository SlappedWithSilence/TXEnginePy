from typing import Dict

from txengine.structures.enums import InputType
from txengine.structures.messages import Frame
from txengine.systems.managers.engine import Engine

from fastapi import FastAPI

# Define constants
app_server: FastAPI = FastAPI()
game_logic: Engine = Engine()
error_frame = Frame(components={"content": "Error! Unable to retrieve Frame!"},
                    input_type=InputType.AFFIRMATIVE,
                    frame_type="Error", input_range={})


# Define helper functions
def init_debug() -> None:
    """Perform pre-game debugging functions"""


def init() -> None:
    """Initialize various engine elements"""


# Define FastAPI functions
@app_server.get("/")
async def root():
    return game_logic.get_frame() or error_frame
