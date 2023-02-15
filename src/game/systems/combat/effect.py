import dataclasses
from abc import ABC

from game.systems.entity.entities import Entity


@dataclasses.dataclass
class Effect(ABC):
    """
    A container for item and combat effects. Effects are usually executing Events
    """

    def perform(self, target: Entity):
        """
        Execute the logic of the Effect
        """
        raise NotImplementedError()
