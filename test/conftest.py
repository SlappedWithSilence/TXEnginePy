"""
A file that contains configuration and utility code pertaining to PyTest
"""

import sys
from loguru import logger

logger.info("Modifying sys.path...")
sys.path.insert(0, '../src')