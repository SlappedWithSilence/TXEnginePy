import pytest
from loguru import logger


def setup_module():
    logger.info("Setting up Currency tests...")
    import game  # Needed to force engine initialization
    from game.systems.currency import currency_manager
    from game.systems.currency import Currency

    currency_manager.currencies[-110] = Currency(-110, "USD", {"cents": 1, "dollars": 100})

    currency_manager.currencies[-111] = Currency(-111, "Imperial",
                                              {
                                                  "bronze": 1,
                                                  "silver": 1000,
                                                  "gold": 1000000
                                              })


def teardown_module():
    """revert the state """
    logger.info("Tearing down Currency tests...")
    from game.systems.currency import currency_manager
    currency_manager.currencies.pop(-110)
    currency_manager.currencies.pop(-111)
