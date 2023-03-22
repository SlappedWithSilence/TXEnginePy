"""
A file that contains configuration and utility code pertaining to PyTest
"""

import sys

import pytest
from loguru import logger

from game import engine, state_device_controller


def pytest_configure(config):
    logger.info("Modifying sys.path...")
    sys.path.insert(0, 'src')
