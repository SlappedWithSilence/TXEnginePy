from abc import ABC


class PhaseHandler(ABC):

    def __init__(self):
        pass

    def handle_phase(self, combat_engine) -> None:
        raise NotImplementedError()
