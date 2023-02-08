from fastapi import FastAPI
from loguru import logger

tx_engine = FastAPI()  # FastAPI service object that hosts TXEngine


# Implement service logic
@tx_engine.get("/")
async def root():
    return "Implement Me!"


# Begin service logic
if __name__ == "__main__":
    logger.info("Starting main...")
    pass
