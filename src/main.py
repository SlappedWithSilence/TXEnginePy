import game

from fastapi import FastAPI
from loguru import logger

from timeit import default_timer

from game.structures.state_device import FiniteStateDevice

tx_engine = FastAPI()  # FastAPI service object that hosts TXEngine


# Implement service logic
@tx_engine.get("/")
def root():
    start = default_timer()
    r = game.state_device_controller.get_current_frame()
    duration = default_timer() - start
    logger.info(f"Completed state retrieval in {duration}s")
    return r


@tx_engine.put("/")
def root(user_input: int | str):
    start = default_timer()
    r = game.state_device_controller.deliver_input(user_input)
    duration = default_timer() - start
    logger.info(f"Completed input submission in {duration}s")
    return r


@tx_engine.get("/dump")
def root():
    device = game.state_device_controller._get_state_device()

    logger.info("******************************************")
    logger.info(f"name: {device.name}")
    logger.info(f"input_type: {device.input_type}")
    logger.info(f"max: {device.domain_max}")
    logger.info(f"min: {device.domain_min}")
    logger.info(f"len: {device.domain_length}")

    if isinstance(device, FiniteStateDevice):

        logger.info(f"current_state: {device.current_state}")
        logger.info(device.state_data)

    logger.info("******************************************")

# Begin service logic
if __name__ == "__main__":
    logger.info("Starting main...")
    pass
