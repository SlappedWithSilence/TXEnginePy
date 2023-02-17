import dataclasses
from abc import ABC

import game.systems.entity as entity


@dataclasses.dataclass
class Effect(ABC):
    """
    A container for item and combat effects. Effects are usually executing Events
    """

    def perform(self, target: entity.entities.Entity):
        """
        Execute the logic of the Effect
        """
        raise NotImplementedError()
