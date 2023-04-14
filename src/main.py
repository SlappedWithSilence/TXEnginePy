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


@tx_engine.get("/cache")
def root(cache_path: str):
    from game.cache import get_cache
    obj: any = get_cache()
    count: int = 0

    if cache_path == r".":
        return str(obj)

    try:
        for key in cache_path.split('.'):
            obj = obj[key]
            count += 1

        return str(obj)
    except KeyError:
        logger.warning("Failed to retrieve")
        return f"No value located at {cache_path}! Traveled to {'.'.join(cache_path.split('.')[:count])}"


# Begin service logic
if __name__ == "__main__":
    logger.info("Starting main...")
    pass
