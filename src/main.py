import game

from fastapi import FastAPI
from loguru import logger

tx_engine = FastAPI()  # FastAPI service object that hosts TXEngine


# Implement service logic
@tx_engine.get("/")
def root():
    return game.state_device_controller.get_current_frame()


@tx_engine.put("/")
def root(user_input: int | str):
    return game.state_device_controller.deliver_input(user_input)


# Begin service logic
if __name__ == "__main__":
    logger.info("Starting main...")
    pass
