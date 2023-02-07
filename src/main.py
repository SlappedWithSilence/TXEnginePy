from fastapi import FastAPI

tx_engine = FastAPI()  # FastAPI service object that hosts TXEngine


# Implement service logic
@tx_engine.get("/")
async def root():
    return "Implement Me!"


# Begin service logic
if __name__ == "__main__":
    pass
