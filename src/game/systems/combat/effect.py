import dataclasses
from abc import ABC




@dataclasses.dataclass
class Effect(ABC):
    """
    A container for item and combat effects. Effects are usually executing Events
    """

    def perform(self, target):
        """
        Execute the logic of the Effect
        """
        raise NotImplementedError()
