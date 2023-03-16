from enum import Enum

from game.structures.enums import InputType
from game.structures.state_device import FiniteStateDevice

import pytest


class MockFiniteStateDevice(FiniteStateDevice):
    class States(Enum):
        DEFAULT = -1

    def __init__(self, default_input_type: InputType, states: Enum, default_state):
        super().__init__(default_input_type, states, default_state)
