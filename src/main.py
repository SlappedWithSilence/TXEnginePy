from fastapi import FastAPI
from loguru import logger

from game import state_device_controller

tx_engine = FastAPI()  # FastAPI service object that hosts TXEngine


# Implement service logic
@tx_engine.get("/")
def root():
    return state_device_controller.get_current_frame()


@tx_engine.put("/")
def root(user_input: str | int):
    return state_device_controller.deliver_input(user_input)


# Begin service logic
if __name__ == "__main__":
    logger.info("Starting main...")
    pass
