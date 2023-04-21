from .engine import Engine
from .game_state_controller import GameStateController

engine: Engine = None
if engine is None:
    engine = Engine()

state_device_controller: GameStateController = GameStateController()
